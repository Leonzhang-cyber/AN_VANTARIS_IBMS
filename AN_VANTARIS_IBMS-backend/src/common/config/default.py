# src/common/config/default.py
import os
from urllib.parse import urlparse, unquote

# Development-only fallbacks — production must set IBMS_SECRET_KEY / IBMS_JWT_SECRET
_DEV_FLASK_SECRET_KEY = "dev-only-flask-secret-do-not-use-in-production"
_DEV_JWT_SECRET_KEY = "dev-only-jwt-secret-do-not-use-in-production"

# Development-only DID fallback — no real private key; production must set IBMS_DID_PRIVATE_KEY
_DEV_DID_PRIVATE_KEY = ""

# Development-only DB fallbacks — production must set IBMS_DATABASE_URL or DB component vars
_DEV_DB_USER = "ibms_user"
_DEV_DB_PASSWORD = "replace-with-db-password"
_DEV_DB_HOST = "127.0.0.1"
_DEV_DB_PORT = "3306"
_DEV_DB_NAME = "ibms_db"

# Development-only MQTT fallbacks — production must set IBMS_MQTT_*
_DEV_MQTT_HOST = "127.0.0.1"
_DEV_MQTT_PORT = "1883"
_DEV_MQTT_USERNAME = "replace-with-mqtt-user"
_DEV_MQTT_PASSWORD = "replace-with-mqtt-password"


def _env_secret(name: str, dev_fallback: str) -> str:
    value = os.getenv(name)
    if value is not None and str(value).strip():
        return str(value).strip()
    return dev_fallback


def _env_str(name: str, dev_fallback: str) -> str:
    value = os.getenv(name)
    if value is not None and str(value).strip():
        return str(value).strip()
    return dev_fallback


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None or not str(value).strip():
        return default
    return str(value).strip().lower() in ("1", "true", "yes", "on")


def normalize_database_uri(url: str) -> str:
    """Ensure PostgreSQL URLs use the psycopg3 SQLAlchemy driver when needed."""
    normalized = str(url).strip()
    if normalized.startswith("postgres://"):
        return "postgresql+psycopg://" + normalized[len("postgres://") :]
    if normalized.startswith("postgresql://"):
        return "postgresql+psycopg://" + normalized[len("postgresql://") :]
    return normalized


def _build_db_config() -> dict:
    database_url = os.getenv("IBMS_DATABASE_URL")
    if database_url is not None and str(database_url).strip():
        url = str(database_url).strip()
        parsed = urlparse(url)
        user = unquote(parsed.username) if parsed.username else _DEV_DB_USER
        password = unquote(parsed.password) if parsed.password else _DEV_DB_PASSWORD
        host = parsed.hostname or _DEV_DB_HOST
        port = str(parsed.port) if parsed.port else _DEV_DB_PORT
        name = (parsed.path or f"/{_DEV_DB_NAME}").lstrip("/") or _DEV_DB_NAME
        return {
            "DB_USER": user,
            "DB_PASSWORD": password,
            "DB_HOST": host,
            "DB_PORT": port,
            "DB_NAME": name,
            "SQLALCHEMY_DATABASE_URI": normalize_database_uri(url),
        }

    user = _env_str("IBMS_DB_USER", _DEV_DB_USER)
    password = _env_secret("IBMS_DB_PASSWORD", _DEV_DB_PASSWORD)
    host = _env_str("IBMS_DB_HOST", _DEV_DB_HOST)
    port = _env_str("IBMS_DB_PORT", _DEV_DB_PORT)
    name = _env_str("IBMS_DB_NAME", _DEV_DB_NAME)
    uri = f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"
    return {
        "DB_USER": user,
        "DB_PASSWORD": password,
        "DB_HOST": host,
        "DB_PORT": port,
        "DB_NAME": name,
        "SQLALCHEMY_DATABASE_URI": uri,
    }


_db = _build_db_config()


class Config:
    # Database — prefer IBMS_DATABASE_URL or IBMS_DB_* (see .env.example)
    DB_USER = _db["DB_USER"]
    DB_PASSWORD = _db["DB_PASSWORD"]
    DB_HOST = _db["DB_HOST"]
    DB_PORT = _db["DB_PORT"]
    DB_NAME = _db["DB_NAME"]
    SQLALCHEMY_DATABASE_URI = _db["SQLALCHEMY_DATABASE_URI"]

    system_did = "did:imbs:system:root:e75d57e76dc8"
    # system_did_secret = "0xa1eeD703B79f2548eaa1E591370d19c67E561D9e"
    system_did_public_key = "0xdA9497EAFF812aF112F26FD162d8e2879e886477"
    system_did_private_key = _env_secret("IBMS_DID_PRIVATE_KEY", _DEV_DID_PRIVATE_KEY)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask / JWT — prefer IBMS_SECRET_KEY / IBMS_JWT_SECRET (see .env.example)
    SECRET_KEY = _env_secret("IBMS_SECRET_KEY", _DEV_FLASK_SECRET_KEY)
    JWT_SECRET_KEY = _env_secret("IBMS_JWT_SECRET", _DEV_JWT_SECRET_KEY)
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 8

    # MQTT — prefer IBMS_MQTT_* (see .env.example)
    MQTT_BROKER_HOST = _env_str("IBMS_MQTT_HOST", _DEV_MQTT_HOST)
    MQTT_BROKER_PORT = int(_env_str("IBMS_MQTT_PORT", _DEV_MQTT_PORT))
    MQTT_USERNAME = _env_str("IBMS_MQTT_USERNAME", _DEV_MQTT_USERNAME)
    MQTT_PASSWORD = _env_secret("IBMS_MQTT_PASSWORD", _DEV_MQTT_PASSWORD)

    # Environment / feature flags (SECURITY-A8: production disables simulators by default)
    IBMS_ENV = _env_str("IBMS_ENV", "development").strip().lower()
    IS_PRODUCTION = IBMS_ENV == "production"
    IS_LOCAL_SMOKE = IBMS_ENV == "local-smoke"
    _raw_simulator_enabled = _env_bool("IBMS_SIMULATOR_ENABLED", False)
    _raw_testmqtt_enabled = _env_bool("IBMS_TESTMQTT_ENABLED", False)
    SIMULATOR_ENABLED = False if IS_PRODUCTION else _raw_simulator_enabled
    TESTMQTT_ENABLED = False if IS_PRODUCTION else _raw_testmqtt_enabled

    # Local smoke bind defaults (override with IBMS_BIND_HOST / IBMS_BIND_PORT)
    BIND_HOST = _env_str("IBMS_BIND_HOST", "127.0.0.1" if IS_LOCAL_SMOKE else "0.0.0.0")
    BIND_PORT = int(_env_str("IBMS_BIND_PORT", "5001" if IS_LOCAL_SMOKE else "5000"))