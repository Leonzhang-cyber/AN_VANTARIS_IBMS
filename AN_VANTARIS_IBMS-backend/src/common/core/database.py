# src/common/core/database.py
from flask_sqlalchemy import SQLAlchemy

# 导入应用配置（确保路径正确）
try:
    from src.common.config.default import Config as AppConfig
except ImportError:
    raise RuntimeError("❌ 无法导入配置类：src.config.default.Config，请检查项目路径。")

# 声明全局 db 实例，延迟初始化
db = SQLAlchemy()


def init_database(app) -> None:
    """
    初始化数据库连接。

    - 从 AppConfig 手动构建数据库 URI，避免依赖 app.config 的加载顺序。
    - 注册 db 到 Flask 应用。
    - 在 DEBUG 模式下主动测试连接，便于快速发现配置或网络问题。
    """
    # 构造数据库连接 URI
    uri = (
        f"mysql+pymysql://{AppConfig.DB_USER}:{AppConfig.DB_PASSWORD}"
        f"@{AppConfig.DB_HOST}:{AppConfig.DB_PORT}/{AppConfig.DB_NAME}"
    )

    # 配置 Flask-SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 绑定 SQLAlchemy 实例到应用
    db.init_app(app)