"""
文件路径: src/data_modeling/csv_storage.py
CSV文件存储管理
"""

import os
import csv
import pandas as pd
from datetime import datetime
from threading import Lock
from queue import Queue
import threading
from typing import Dict, List, Optional

from src.data_modeling.config import CSV_CONFIG
from src.data_modeling.exceptions import CSVWriteError


class CSVStorage:
    """设备数据CSV存储管理器（线程安全）"""

    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or CSV_CONFIG['data_dir']
        self.write_queue = Queue()
        self.device_locks = {}
        self.lock = Lock()
        self._running = True

        os.makedirs(self.data_dir, exist_ok=True)
        self._start_worker()

    def _get_device_path(self, device_code: str) -> str:
        """获取设备CSV文件路径（使用 device_code）"""
        return os.path.join(self.data_dir, f"{device_code}.csv")

    def _get_device_lock(self, device_code: str) -> Lock:
        """获取设备级别的锁"""
        with self.lock:
            if device_code not in self.device_locks:
                self.device_locks[device_code] = Lock()
            return self.device_locks[device_code]

    def append_data(self, device_code: str, standard_data: Dict):
        """异步写入数据（非阻塞）"""
        if not standard_data:
            return
        self.write_queue.put((device_code, standard_data.copy()))

    def _write_row(self, device_code: str, data: Dict):
        """实际写入CSV（带锁）- 优化版：只检查最后一条记录"""
        file_path = self._get_device_path(device_code)
        lock = self._get_device_lock(device_code)

        with lock:
            # 确保有时间戳
            if 'timestamp' not in data:
                data['timestamp'] = datetime.now().isoformat()

            file_exists = os.path.exists(file_path)

            if not file_exists:
                # 文件不存在，直接写入
                with open(file_path, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=data.keys())
                    writer.writeheader()
                    writer.writerow(data)
                print(f"[CSV] 创建并写入: {device_code}")
                return

            # 检查最后一条记录的时间戳
            last_row = pd.read_csv(file_path).tail(1)

            if not last_row.empty:
                last_timestamp = pd.to_datetime(last_row['timestamp'].iloc[0])
                new_timestamp = pd.to_datetime(data['timestamp'])

                if last_timestamp == new_timestamp:
                    # 时间相同：需要覆盖（需要读取整个文件）
                    df = pd.read_csv(file_path, parse_dates=['timestamp'])
                    mask = df['timestamp'] == new_timestamp
                    df.loc[mask, list(data.keys())] = [data.get(k) for k in df.columns if k in data]
                    df.to_csv(file_path, index=False, encoding='utf-8')
                    print(f"[CSV] 覆盖写入: {device_code}")
                    return

            # 时间不同，直接追加
            with open(file_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data.keys())
                writer.writerow(data)
            print(f"[CSV] 追加写入: {device_code}")

    def _start_worker(self):
        """启动后台写入线程"""

        def worker():
            while self._running:
                try:
                    device_code, data = self.write_queue.get(timeout=1)
                    try:
                        self._write_row(device_code, data)
                    except CSVWriteError as e:
                        print(f"CSV写入失败: {e}")
                    except Exception as e:
                        print(f"未知错误: {e}")
                except:
                    pass

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def read_dataframe(self, device_code: str) -> pd.DataFrame:
        """读取CSV为DataFrame"""
        file_path = self._get_device_path(device_code)
        if not os.path.exists(file_path):
            return pd.DataFrame()

        df = pd.read_csv(file_path, parse_dates=['timestamp'])
        return df

    def read_dataframe_range(self, device_code: str,
                             start_time: str = None,
                             end_time: str = None,
                             limit: int = None) -> pd.DataFrame:
        """按时间范围读取DataFrame"""
        df = self.read_dataframe(device_code)
        if df.empty:
            return df

        if start_time:
            df = df[df['timestamp'] >= start_time]
        if end_time:
            df = df[df['timestamp'] <= end_time]
        if limit:
            df = df.tail(limit)

        return df

    def get_data_count(self, device_code: str) -> int:
        """获取设备数据条数"""
        file_path = self._get_device_path(device_code)
        if not os.path.exists(file_path):
            return 0

        df = pd.read_csv(file_path)
        return len(df)

    def get_available_fields(self, device_code: str) -> List[str]:
        """获取设备CSV中可用的字段列表"""
        df = self.read_dataframe(device_code)
        if df.empty:
            return []
        # 排除不适合作为特征的字段
        exclude_fields = ['device_code', 'device_did', 'seq']

        return [col for col in df.columns if col not in exclude_fields]

    def get_latest_data(self, device_code: str) -> Optional[Dict]:
        """获取设备最新一条数据"""
        df = self.read_dataframe(device_code)
        if df.empty:
            return None

        latest = df.iloc[-1].to_dict()
        # 转换timestamp为字符串
        if 'timestamp' in latest:
            latest['timestamp'] = str(latest['timestamp'])
        return latest

    def delete_device_data(self, device_code: str) -> bool:
        """删除设备的所有CSV数据"""
        file_path = self._get_device_path(device_code)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    def stop(self):
        """停止后台写入"""
        self._running = False


# 全局单例
csv_storage = CSVStorage()