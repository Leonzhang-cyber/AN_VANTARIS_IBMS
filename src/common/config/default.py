# config/default.py

class Config:
    # 🔒 直接写死数据库连接信息（仅限本地/私有开发！）
    DB_USER = "ibms"
    DB_PASSWORD = "hexin.com"
    DB_HOST = "140.245.109.223"
    DB_PORT = "13306"
    DB_NAME = "ibms"

    # 构造完整的 SQLAlchemy 数据库 URI
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT 配置
    JWT_SECRET_KEY = "your-secret-key-change-in-production"  # 生产环境务必使用强随机密钥
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 8

    # MQTT Broker 配置
    MQTT_BROKER_HOST = '1.14.152.252'
    MQTT_BROKER_PORT = 1883
    # MQTT_BROKER_HOST = 'broker.emqx.io'
    # MQTT_BROKER_PORT = 8084