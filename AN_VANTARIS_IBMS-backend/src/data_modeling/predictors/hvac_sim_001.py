"""
文件路径: src/data_modeling/predictors/hvac_sim_001.py
HVAC 设备预测器 - 完整预测逻辑
适配字段: temperature, power, outdoor_temperature, set_temperature,
         occupancy, holiday_flag, solar_radiation, chiller_state

注意: 此模块不接收 device_code 参数，由 service 层根据设备号定位到此模块
"""

import os
import joblib
import numpy as np
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.feature_selection import SelectKBest, f_regression
import xgboost as xgb

# ==================== 配置 ====================

# 城市坐标映射
CITY_COORDS = {
    "Beijing": {"lat": 39.9042, "lon": 116.4074},
    "Singapore": {"lat": 1.3521, "lon": 103.8198},
    "Hong Kong": {"lat": 22.3193, "lon": 114.1694},
    "Shanghai": {"lat": 31.2304, "lon": 121.4737},
    "Shenzhen": {"lat": 22.5431, "lon": 114.0579}
}

# 默认配置
DEFAULT_CONFIG = {
    "city": "Hong Kong",
    "electricity_price": 1.44,
    "enable_saving": True
}

# 模型保存时会使用的标识（用于生成文件名）
MODEL_ID = "hvac"


# ==================== 数据预处理 ====================

def load_and_preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    加载并预处理数据
    适配字段名: temperature, outdoor_temperature, power, etc.
    """
    df = df.copy()

    # 删除不需要的字段
    drop_cols = ['device_code', 'device_did', 'seq']
    for col in drop_cols:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)

    # 确保有时间戳并设为索引
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)

    # 字段名映射（适配你的CSV -> 算法期望的字段名）
    column_mapping = {
        'temperature': 'zone_1_temp',
        'outdoor_temperature': 'outdoor_air_temp',
        'set_temperature': 'chilled_water_temp_setpoint',
        'power': 'chiller_A_power_kW',
        'solar_radiation': 'solar_radiation_w_m2',
        'chiller_state': 'chiller_A_status',
        'holiday_flag': 'is_holiday'
    }

    for old_name, new_name in column_mapping.items():
        if old_name in df.columns and new_name not in df.columns:
            df.rename(columns={old_name: new_name}, inplace=True)

    # 插值缺失值
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].interpolate(method='linear', limit_direction='both')

    # 布尔字段填充
    if 'is_holiday' in df.columns:
        df['is_holiday'] = df['is_holiday'].fillna(False)

    return df


# ==================== 特征工程 ====================

def create_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """创建时间特征"""
    df = df.copy()
    df['hour'] = df.index.hour
    df['day_of_week'] = df.index.dayofweek
    df['month'] = df.index.month
    df['day_of_year'] = df.index.dayofyear
    df['weekend'] = (df['day_of_week'] >= 5).astype(int)

    # 周期编码
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)

    # 时段特征
    def get_period(hour):
        if 6 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 18:
            return 'afternoon'
        elif 18 <= hour < 22:
            return 'evening'
        else:
            return 'night'

    df['time_period'] = df['hour'].apply(get_period)
    df = pd.get_dummies(df, columns=['time_period'], prefix='period')

    return df


def create_weather_features(df: pd.DataFrame) -> pd.DataFrame:
    """创建天气相关特征"""
    df = df.copy()

    if 'zone_1_temp' in df.columns and 'outdoor_air_temp' in df.columns:
        df['temp_difference'] = df['zone_1_temp'] - df['outdoor_air_temp']
        df['temp_difference_abs'] = np.abs(df['temp_difference'])

    if 'outdoor_air_temp' in df.columns and 'solar_radiation_w_m2' in df.columns:
        df['temp_radiation_interaction'] = df['outdoor_air_temp'] * df['solar_radiation_w_m2'] / 100

    if 'outdoor_air_temp' in df.columns and 'dew_point_temp' in df.columns:
        df['temp_dew_point_diff'] = df['outdoor_air_temp'] - df['dew_point_temp']

    return df


def create_rolling_features(df: pd.DataFrame, windows=[4, 12, 24, 48]) -> pd.DataFrame:
    """创建滚动统计特征"""
    df = df.copy()

    if 'chiller_A_power_kW' in df.columns:
        for w in windows:
            df[f'power_rolling_mean_{w}'] = df['chiller_A_power_kW'].rolling(w, min_periods=1).mean()

    if 'outdoor_air_temp' in df.columns:
        for w in windows:
            df[f'temp_rolling_mean_{w}'] = df['outdoor_air_temp'].rolling(w, min_periods=1).mean()

    return df


def full_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """完整的特征工程流程"""
    df = create_time_features(df)
    df = create_weather_features(df)
    df = create_rolling_features(df)
    df = df.dropna()
    return df


# ==================== 模型训练 ====================

def train_model(df_processed: pd.DataFrame):
    """
    训练 XGBoost + 校准模型
    返回: (model, calibration_model, selected_features, metrics)
    """
    # 排除的列（包括不需要的字段）
    EXCLUDED_COLS = [
        'chiller_A_power_kW',        # 目标变量
    ]

    all_cols = df_processed.columns
    feature_candidates = [
        c for c in all_cols
        if c not in EXCLUDED_COLS
        and df_processed[c].dtype in ['float64', 'int64', 'bool']
    ]

    X = df_processed[feature_candidates]
    y = df_processed['chiller_A_power_kW']

    # 时序划分（80% 训练，20% 测试）
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    # 特征选择
    k = min(20, len(feature_candidates))
    selector = SelectKBest(f_regression, k=k)
    selector.fit(X_train, y_train)
    selected_idx = selector.get_support(indices=True)
    selected_feats = [feature_candidates[i] for i in selected_idx]

    X_train_sel = X_train[selected_feats]
    X_test_sel = X_test[selected_feats]

    # 训练 XGBoost
    xgb_model = xgb.XGBRegressor(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=3,
        random_state=42,
        n_jobs=-1,
        verbosity=0
    )
    xgb_model.fit(X_train_sel, y_train)

    # 预测并校准
    y_pred = xgb_model.predict(X_test_sel)
    y_pred = np.maximum(y_pred, 0)

    # 线性校准
    cal_model = LinearRegression()
    cal_model.fit(y_pred.reshape(-1, 1), y_test)

    # 评估指标
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(((y_test - y_pred) ** 2).mean())

    metrics = {
        "r2": round(r2, 4),
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "features_count": len(selected_feats)
    }

    return xgb_model, cal_model, selected_feats, metrics


# ==================== 天气数据获取 ====================

def get_historical_weather(start_date, end_date, lat, lon, city_name):
    """获取历史天气数据"""
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ["temperature_2m", "shortwave_radiation", "dew_point_2m"],
        "timezone": "Asia/Shanghai"
    }
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        hourly = data['hourly']
        timestamps = pd.to_datetime(hourly['time'])
        df = pd.DataFrame({
            'timestamp': timestamps,
            'outdoor_air_temp': hourly['temperature_2m'],
            'dew_point_temp': hourly['dew_point_2m'],
            'solar_radiation_w_m2': hourly['shortwave_radiation'],
        })
        print(f"📅 获取历史天气成功 ({city_name}, {len(df)} 条)")
        return df
    except Exception as e:
        print(f"⚠️ 历史天气获取失败: {e}")
        return None


def get_weather_forecast(days, lat, lon, city_name):
    """获取天气预报"""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["temperature_2m", "shortwave_radiation", "dew_point_2m"],
        "forecast_days": days,
        "timezone": "Asia/Shanghai"
    }
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        hourly = data['hourly']
        timestamps = pd.to_datetime(hourly['time'])
        df = pd.DataFrame({
            'timestamp': timestamps,
            'outdoor_air_temp': hourly['temperature_2m'],
            'dew_point_temp': hourly['dew_point_2m'],
            'solar_radiation_w_m2': hourly['shortwave_radiation'],
        })
        print(f"🌤️ 获取天气预报成功 ({city_name}, {len(df)} 条)")
        return df
    except Exception as e:
        print(f"⚠️ 天气预报获取失败: {e}")
        return None


def generate_simulated_weather(start_date, end_date, lat, lon, city_name, hist_df):
    """生成模拟天气（基于历史数据）"""
    print(f"🧪 生成模拟天气: {start_date.date()} 至 {end_date.date()}")

    if hist_df is None or hist_df.empty:
        # 如果没有历史数据，生成简单模拟
        hours = int((end_date - start_date).total_seconds() / 3600) + 24
        timestamps = [start_date + timedelta(hours=i) for i in range(hours)]
        records = []
        for dt in timestamps:
            hour = dt.hour
            records.append({
                'timestamp': dt,
                'outdoor_air_temp': 20 + 5 * np.sin(2 * np.pi * (hour - 14) / 24),
                'dew_point_temp': 15 + 3 * np.sin(2 * np.pi * (hour - 14) / 24),
                'solar_radiation_w_m2': max(0, 500 * np.sin(np.pi * (hour - 6) / 12)) if 6 <= hour <= 18 else 0
            })
        return pd.DataFrame(records)

    # 基于历史数据生成
    hist_df['timestamp'] = pd.to_datetime(hist_df['timestamp'])
    records = []
    for _, row in hist_df.iterrows():
        new_ts = row['timestamp'] + timedelta(days=365)
        if start_date <= new_ts <= end_date:
            records.append({
                'timestamp': new_ts,
                'outdoor_air_temp': row['outdoor_air_temp'] + np.random.normal(0, 0.5),
                'dew_point_temp': row['dew_point_temp'] + np.random.normal(0, 0.5),
                'solar_radiation_w_m2': max(0, row['solar_radiation_w_m2'] * np.random.uniform(0.9, 1.1))
            })

    return pd.DataFrame(records)


def get_weather_data(start_time: datetime, days: int, city: str, hist_weather_df: pd.DataFrame = None) -> pd.DataFrame:
    """三级降级获取天气数据"""
    coords = CITY_COORDS.get(city, CITY_COORDS["Hong Kong"])
    current_date = datetime.now().date()
    end_date = (start_time + timedelta(days=days - 1)).date()

    weather_segments = []

    # 1. 历史部分
    hist_start = start_time.date()
    hist_end = min(end_date, current_date - timedelta(days=1))
    if hist_start <= hist_end:
        df = get_historical_weather(
            hist_start.strftime('%Y-%m-%d'),
            hist_end.strftime('%Y-%m-%d'),
            coords['lat'], coords['lon'], city
        )
        if df is not None and not df.empty:
            weather_segments.append(df)

    # 2. 预报部分
    forecast_start = current_date
    forecast_end = min(end_date, current_date + timedelta(days=15))
    if forecast_start <= forecast_end:
        days_needed = (forecast_end - forecast_start).days + 1
        df = get_weather_forecast(days_needed, coords['lat'], coords['lon'], city)
        if df is not None and not df.empty:
            mask = (df['timestamp'].dt.date >= forecast_start) & (df['timestamp'].dt.date <= forecast_end)
            df = df[mask].copy()
            if not df.empty:
                weather_segments.append(df)

    # 3. 模拟部分
    sim_start = forecast_end + timedelta(days=1)
    sim_end = end_date
    if sim_start <= sim_end:
        sim_start_dt = datetime.combine(sim_start, datetime.min.time())
        sim_end_dt = datetime.combine(sim_end, datetime.min.time())
        df = generate_simulated_weather(sim_start_dt, sim_end_dt, coords['lat'], coords['lon'], city, hist_weather_df)
        if df is not None and not df.empty:
            weather_segments.append(df)

    if not weather_segments:
        raise ValueError("无法获取任何天气数据")

    # 合并
    weather_df = pd.concat(weather_segments, ignore_index=True)
    weather_df = weather_df.drop_duplicates(subset=['timestamp']).sort_values('timestamp').reset_index(drop=True)

    return weather_df


# ==================== 递归预测器 ====================

class IterativePredictor:
    """递归预测器"""

    def __init__(self, model, cal_model, features, hist_df):
        self.model = model
        self.cal_model = cal_model
        self.features = features
        self.hist = hist_df
        self._compute_stats()

    def _compute_stats(self):
        """计算历史统计特征"""
        self.hourly_avg_temp = self.hist.groupby(self.hist.index.hour)['outdoor_air_temp'].mean() if 'outdoor_air_temp' in self.hist.columns else pd.Series(20, index=range(24))
        self.hourly_avg_rad = self.hist.groupby(self.hist.index.hour)['solar_radiation_w_m2'].mean() if 'solar_radiation_w_m2' in self.hist.columns else pd.Series(200, index=range(24))
        self.avg_zone_temp = self.hist['zone_1_temp'].mean() if 'zone_1_temp' in self.hist.columns else 22
        self.recent_power_avg = self.hist['chiller_A_power_kW'].iloc[-96:].mean() if len(self.hist) >= 96 else self.hist['chiller_A_power_kW'].mean()

    def _get_features(self, timestamp, weather_row, predicted_history):
        """构建预测特征"""
        features = {}

        # 时间特征
        features['hour'] = timestamp.hour
        features['day_of_week'] = timestamp.weekday()
        features['month'] = timestamp.month
        features['day_of_year'] = timestamp.timetuple().tm_yday
        features['weekend'] = 1 if timestamp.weekday() >= 5 else 0
        features['hour_sin'] = np.sin(2 * np.pi * timestamp.hour / 24)
        features['hour_cos'] = np.cos(2 * np.pi * timestamp.hour / 24)
        features['month_sin'] = np.sin(2 * np.pi * timestamp.month / 12)
        features['month_cos'] = np.cos(2 * np.pi * timestamp.month / 12)

        # 时段特征
        for p in ['morning', 'afternoon', 'evening', 'night']:
            features[f'period_{p}'] = 1 if ((p == 'morning' and 6 <= timestamp.hour < 12) or
                                            (p == 'afternoon' and 12 <= timestamp.hour < 18) or
                                            (p == 'evening' and 18 <= timestamp.hour < 22) or
                                            (p == 'night' and not (6 <= timestamp.hour < 22))) else 0

        # 天气特征
        features['outdoor_air_temp'] = weather_row.get('outdoor_air_temp', 20)
        features['solar_radiation_w_m2'] = weather_row.get('solar_radiation_w_m2', 200)
        features['dew_point_temp'] = weather_row.get('dew_point_temp', 15)
        features['temp_difference'] = self.avg_zone_temp - features['outdoor_air_temp']
        features['temp_difference_abs'] = np.abs(features['temp_difference'])
        features['temp_radiation_interaction'] = features['outdoor_air_temp'] * features['solar_radiation_w_m2'] / 100
        features['temp_dew_point_diff'] = features['outdoor_air_temp'] - features['dew_point_temp']

        # 历史统计
        features['hourly_avg_temp'] = self.hourly_avg_temp.get(timestamp.hour, 20)
        features['hourly_avg_radiation'] = self.hourly_avg_rad.get(timestamp.hour, 200)

        if len(predicted_history) >= 96:
            features['recent_avg_power'] = np.mean(predicted_history[-96:])
        else:
            features['recent_avg_power'] = self.recent_power_avg

        # 滚动特征
        for w in [4, 12, 24, 48]:
            features[f'temp_rolling_mean_{w}'] = features['outdoor_air_temp']

        # 滞后特征
        for lag in [1, 2, 3, 4, 6, 8, 12, 24]:
            features[f'outdoor_temp_lag_{lag}'] = features['outdoor_air_temp']

        # 确保所有特征存在
        X = np.array([features.get(f, 0) for f in self.features])
        return X.reshape(1, -1)

    def predict_horizon(self, start_time, weather_df, hours):
        """递归预测"""
        predicted_power = []
        results = []

        weather_dict = {row['timestamp']: row for _, row in weather_df.iterrows()}

        for i in range(hours):
            dt = start_time + timedelta(hours=i)

            if dt in weather_dict:
                weather_row = weather_dict[dt]
            else:
                weather_row = weather_df.iloc[-1].to_dict()

            X_feat = self._get_features(dt, weather_row, predicted_power)
            pred = self.model.predict(X_feat)[0]

            # 校准
            if self.cal_model:
                pred = self.cal_model.predict([[pred]])[0]
            pred = max(pred, 0)

            predicted_power.append(pred)
            results.append({
                'timestamp': dt,
                'predicted_power_kW': round(pred, 2),
                'outdoor_temp': round(weather_row.get('outdoor_air_temp', 0), 1),
                'solar_radiation': round(weather_row.get('solar_radiation_w_m2', 0), 0)
            })

        return pd.DataFrame(results)


# ==================== 节能模拟 ====================

def apply_saving_strategies(results_df):
    """应用节能策略"""
    df = results_df.copy()
    peak = df['predicted_power_kW'].max()
    low_th = peak * 0.3

    saving_factors = np.ones(len(df)) * 0.95
    low_mask = df['predicted_power_kW'] < low_th
    saving_factors[low_mask] *= 0.5
    cool_mask = df['outdoor_temp'] < 20
    saving_factors[cool_mask] *= 0.97

    df['saving_power_kW'] = df['predicted_power_kW'] * saving_factors
    df['saving_power_kW'] = df['saving_power_kW'].clip(lower=0)

    strategy_info = {
        'chiller_reset_saving_pct': 5,
        'low_load_hours': int(low_mask.sum()),
        'low_load_saving_pct': 50,
        'ahu_optimization_hours': int(cool_mask.sum()),
        'ahu_saving_pct': 3
    }

    return df, strategy_info


# ==================== 主入口函数（供 service 调用） ====================

def train(df: pd.DataFrame, models_dir: str, **kwargs) -> dict:
    """
    训练模型

    参数:
        df: 设备 CSV 数据 (DataFrame)
        models_dir: 模型保存目录
        **kwargs: 其他参数（预留）

    返回:
        dict: 训练结果
    """
    print(f"\n{'='*60}")
    print(f"🚀 开始训练 HVAC 预测模型")
    print(f"{'='*60}")

    # 1. 数据预处理
    print("📊 数据预处理...")
    df_processed = load_and_preprocess_data(df)
    print(f"   原始数据: {len(df)} 条")

    # 2. 特征工程
    print("🔧 特征工程...")
    df_featured = full_feature_engineering(df_processed)
    print(f"   特征工程后: {len(df_featured)} 条")

    if len(df_featured) < 50:
        raise ValueError(f"数据不足，当前{len(df_featured)}条，至少需要50条")

    # 3. 训练模型
    print("🤖 训练模型...")
    model, cal_model, features, metrics = train_model(df_featured)

    # 4. 保存模型
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, f"{MODEL_ID}.pkl")
    joblib.dump({
        'model': model,
        'calibration_model': cal_model,
        'features': features,
        'metrics': metrics,
        'trained_at': datetime.now().isoformat(),
        'historical_data': df_featured
    }, model_path)

    print(f"✅ 训练完成!")
    print(f"   R²: {metrics['r2']}")
    print(f"   MAE: {metrics['mae']} kW")
    print(f"   模型保存至: {model_path}")
    print(f"{'='*60}\n")

    return {
        "message": "训练完成",
        "model_path": model_path,
        "metrics": metrics
    }


def predict_future(device_code: str, days: int, models_dir: str, **kwargs) -> Dict[str, Any]:
    """
    预测未来多天

    参数:
        days: 预测天数
        models_dir: 模型保存目录
        **kwargs: 其他参数 (city, electricity_price, enable_saving)

    返回:
        dict: 预测结果
    """
    print(f"\n{'='*60}")
    print(f"🔮 开始预测 HVAC 能耗, 天数: {days}")
    print(f"{'='*60}")

    # 1. 加载模型
    model_path = os.path.join(models_dir, f"{MODEL_ID}.pkl")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"模型不存在，请先训练: {model_path}")

    model_pkg = joblib.load(model_path)
    model = model_pkg['model']
    cal_model = model_pkg['calibration_model']
    features = model_pkg['features']
    hist_df = model_pkg.get('historical_data')

    # 🆕 2. 获取 CSV 最新数据的时间
    from src.data_modeling.csv_storage import csv_storage
    df = csv_storage.read_dataframe(device_code)
    if df.empty:
        raise ValueError(f"设备 {device_code} 无历史数据")

    latest_timestamp = pd.to_datetime(df['timestamp'].max())
    print(f"📅 CSV 最新数据时间: {latest_timestamp}")

    # 🆕 预测从最新数据的下一个时间点开始（假设15分钟间隔）
    start_time = latest_timestamp + timedelta(minutes=15)
    print(f"🔮 预测开始时间: {start_time}")

    # 3. 获取配置
    city = kwargs.get('city', DEFAULT_CONFIG['city'])
    electricity_price = kwargs.get('electricity_price', DEFAULT_CONFIG['electricity_price'])
    enable_saving = kwargs.get('enable_saving', DEFAULT_CONFIG['enable_saving'])

    # 4. 获取天气数据
    weather_df = get_weather_data(start_time, days, city, hist_df)

    # 5. 递归预测
    hours = days * 24
    predictor = IterativePredictor(model, cal_model, features, hist_df)
    pred_results = predictor.predict_horizon(start_time, weather_df, hours)

    # 5. 计算统计
    pred_results['energy_kWh'] = pred_results['predicted_power_kW'] * 0.25
    total_energy = pred_results['energy_kWh'].sum()
    avg_power = pred_results['predicted_power_kW'].mean()
    peak_power = pred_results['predicted_power_kW'].max()
    min_power = pred_results['predicted_power_kW'].min()
    avg_temp = pred_results['outdoor_temp'].mean()
    estimated_cost = total_energy * electricity_price

    # 6. 按天汇总
    pred_results['date'] = pred_results['timestamp'].dt.date
    daily = pred_results.groupby('date').agg({
        'energy_kWh': 'sum',
        'predicted_power_kW': 'mean',
        'outdoor_temp': 'mean'
    }).reset_index()
    daily['date_str'] = daily['date'].astype(str)
    daily_list = daily[['date_str', 'energy_kWh', 'predicted_power_kW', 'outdoor_temp']].to_dict(orient='records')

    # 7. 构建响应
    response = {
        "status": "success",
        "prediction_stats": {
            "total_energy_kWh": round(total_energy, 1),
            "avg_power_kW": round(avg_power, 1),
            "peak_power_kW": round(peak_power, 1),
            "min_power_kW": round(min_power, 1),
            "avg_outdoor_temp": round(avg_temp, 1),
            "estimated_cost_yuan": round(estimated_cost, 0),
            "start_date": start_time.strftime('%Y-%m-%d'),
            "end_date": (start_time + timedelta(days=days - 1)).strftime('%Y-%m-%d')
        },
        "daily_data": daily_list,
        "raw_hourly_data": pred_results[['timestamp', 'predicted_power_kW', 'outdoor_temp']].to_dict(orient='records')
    }

    # 8. 节能模拟
    if enable_saving:
        saving_df, strategy = apply_saving_strategies(pred_results)
        saving_df['energy_kWh_saving'] = saving_df['saving_power_kW'] * 0.25
        daily_saving = saving_df.groupby('date').agg({'energy_kWh_saving': 'sum'}).reset_index()
        daily_saving.columns = ['date', 'saving_energy_kWh']

        daily_with_saving = daily.merge(daily_saving, on='date', how='left')
        daily_with_saving['saving_energy_kWh'] = daily_with_saving['saving_energy_kWh'].fillna(0)
        total_saving_energy = daily_with_saving['saving_energy_kWh'].sum()
        energy_saved = total_energy - total_saving_energy
        saving_rate = (energy_saved / total_energy * 100) if total_energy > 0 else 0
        cost_saved = energy_saved * electricity_price
        co2_saved_kg = energy_saved * 0.5

        response["saving_simulation"] = {
            "original_energy_kWh": round(total_energy, 1),
            "saving_energy_kWh": round(total_saving_energy, 1),
            "energy_saved_kWh": round(energy_saved, 1),
            "saving_rate_percent": round(saving_rate, 1),
            "cost_saved_yuan": round(cost_saved, 0),
            "co2_saved_kg": round(co2_saved_kg, 0),
            "strategy_details": strategy,
            "daily_comparison": daily_with_saving[['date', 'energy_kWh', 'saving_energy_kWh']].to_dict(orient='records')
        }

    print(f"✅ 预测完成! 总能耗: {total_energy:.1f} kWh")
    print(f"{'='*60}\n")

    return response


def predict(features: Dict[str, float], models_dir: str, **kwargs) -> float:
    """
    单点预测（简化版，用于兼容）

    参数:
        features: 特征值字典
        models_dir: 模型保存目录

    返回:
        float: 预测值
    """
    model_path = os.path.join(models_dir, f"{MODEL_ID}.pkl")
    model_pkg = joblib.load(model_path)
    model = model_pkg['model']
    feature_names = model_pkg['features']

    X = [[features.get(f, 0) for f in feature_names]]
    prediction = model.predict(X)[0]

    return float(prediction)


def get_model_info(models_dir: str) -> dict:
    """获取模型信息"""
    model_path = os.path.join(models_dir, f"{MODEL_ID}.pkl")
    if not os.path.exists(model_path):
        return {"exists": False}

    model_pkg = joblib.load(model_path)
    return {
        "exists": True,
        "metrics": model_pkg.get('metrics'),
        "trained_at": model_pkg.get('trained_at')
    }