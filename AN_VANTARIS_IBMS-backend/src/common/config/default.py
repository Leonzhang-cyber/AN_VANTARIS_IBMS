# src/common/config/default.py
import os
from urllib.parse import urlparse, unquote

# Development-only fallbacks — production must set VANTARIS_ONE_SECRET_KEY /
# VANTARIS_ONE_JWT_SECRET. IBMS_* names remain as legacy compatibility fallback.
_DEV_FLASK_SECRET_KEY = "dev-only-flask-secret-do-not-use-in-production"
_DEV_JWT_SECRET_KEY = "dev-only-jwt-secret-do-not-use-in-production"

# Development-only DID fallback — no real private key; production must set
# VANTARIS_ONE_DID_PRIVATE_KEY. IBMS_* remains as legacy compatibility fallback.
_DEV_DID_PRIVATE_KEY = ""

# Development-only DB fallbacks — production must set VANTARIS_ONE_DATABASE_URL.
# IBMS_DATABASE_URL / IBMS_DB_* remain as legacy compatibility fallback.
_DEV_DB_USER = "ibms_user"
_DEV_DB_PASSWORD = "replace-with-db-password"
_DEV_DB_HOST = "127.0.0.1"
_DEV_DB_PORT = "3306"
_DEV_DB_NAME = "ibms_db"

# Development-only MQTT fallbacks — production must set VANTARIS_ONE_MQTT_*.
# IBMS_MQTT_* remains as legacy compatibility fallback.
_DEV_MQTT_HOST = "127.0.0.1"
_DEV_MQTT_PORT = "1883"
_DEV_MQTT_USERNAME = "replace-with-mqtt-user"
_DEV_MQTT_PASSWORD = "replace-with-mqtt-password"


def _env_first(names: tuple[str, ...], dev_fallback: str) -> str:
    for name in names:
        value = os.getenv(name)
        if value is not None and str(value).strip():
            return str(value).strip()
    return dev_fallback


def _env_secret(names: tuple[str, ...] | str, dev_fallback: str) -> str:
    env_names = (names,) if isinstance(names, str) else names
    return _env_first(env_names, dev_fallback)


def _env_str(names: tuple[str, ...] | str, dev_fallback: str) -> str:
    env_names = (names,) if isinstance(names, str) else names
    return _env_first(env_names, dev_fallback)


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
    database_url = _env_str(
        (
            "VANTARIS_ONE_DATABASE_URL",
            # Legacy compatibility fallback; keep until IBMS_* runtime names are retired.
            "IBMS_DATABASE_URL",
        ),
        "",
    )
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

    # Legacy compatibility fallback for component DB settings.
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
    # Database — prefer VANTARIS_ONE_DATABASE_URL; IBMS_* is legacy fallback.
    DB_USER = _db["DB_USER"]
    DB_PASSWORD = _db["DB_PASSWORD"]
    DB_HOST = _db["DB_HOST"]
    DB_PORT = _db["DB_PORT"]
    DB_NAME = _db["DB_NAME"]
    SQLALCHEMY_DATABASE_URI = _db["SQLALCHEMY_DATABASE_URI"]

    system_did = "did:imbs:system:root:e75d57e76dc8"
    # system_did_secret = "0xa1eeD703B79f2548eaa1E591370d19c67E561D9e"
    system_did_public_key = "0xdA9497EAFF812aF112F26FD162d8e2879e886477"
    system_did_private_key = _env_secret(
        (
            "VANTARIS_ONE_DID_PRIVATE_KEY",
            # Legacy compatibility fallback.
            "IBMS_DID_PRIVATE_KEY",
        ),
        _DEV_DID_PRIVATE_KEY,
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask / JWT — prefer VANTARIS_ONE_*; IBMS_* is legacy fallback.
    SECRET_KEY = _env_secret(
        (
            "VANTARIS_ONE_SECRET_KEY",
            # Legacy compatibility fallback.
            "IBMS_SECRET_KEY",
        ),
        _DEV_FLASK_SECRET_KEY,
    )
    JWT_SECRET_KEY = _env_secret(
        (
            "VANTARIS_ONE_JWT_SECRET",
            # Legacy compatibility fallback.
            "IBMS_JWT_SECRET",
        ),
        _DEV_JWT_SECRET_KEY,
    )
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 8

    # MQTT — prefer VANTARIS_ONE_MQTT_*; IBMS_MQTT_* is legacy fallback.
    MQTT_BROKER_HOST = _env_str(("VANTARIS_ONE_MQTT_HOST", "IBMS_MQTT_HOST"), _DEV_MQTT_HOST)
    MQTT_BROKER_PORT = int(_env_str(("VANTARIS_ONE_MQTT_PORT", "IBMS_MQTT_PORT"), _DEV_MQTT_PORT))
    MQTT_USERNAME = _env_str(("VANTARIS_ONE_MQTT_USERNAME", "IBMS_MQTT_USERNAME"), _DEV_MQTT_USERNAME)
    MQTT_PASSWORD = _env_secret(("VANTARIS_ONE_MQTT_PASSWORD", "IBMS_MQTT_PASSWORD"), _DEV_MQTT_PASSWORD)

    # Environment / feature flags (SECURITY-A8: production disables simulators by default)
    ONE_ENV = _env_str(
        (
            "VANTARIS_ONE_ENV",
            # Legacy compatibility fallback.
            "IBMS_ENV",
        ),
        "development",
    ).strip().lower()
    IBMS_ENV = ONE_ENV
    IS_PRODUCTION = IBMS_ENV == "production"
    IS_LOCAL_SMOKE = IBMS_ENV == "local-smoke"
    _raw_simulator_enabled = _env_bool("IBMS_SIMULATOR_ENABLED", False)
    _raw_testmqtt_enabled = _env_bool("IBMS_TESTMQTT_ENABLED", False)
    SIMULATOR_ENABLED = False if IS_PRODUCTION else _raw_simulator_enabled
    TESTMQTT_ENABLED = False if IS_PRODUCTION else _raw_testmqtt_enabled

    # Local smoke bind defaults (override with VANTARIS_ONE_*; IBMS_* is legacy fallback)
    BIND_HOST = _env_str(
        (
            "VANTARIS_ONE_BIND_HOST",
            # Legacy compatibility fallback.
            "IBMS_BIND_HOST",
        ),
        "127.0.0.1" if IS_LOCAL_SMOKE else "0.0.0.0",
    )
    BIND_PORT = int(
        _env_str(
            (
                "VANTARIS_ONE_BIND_PORT",
                # Legacy compatibility fallback.
                "IBMS_BIND_PORT",
            ),
            "5001" if IS_LOCAL_SMOKE else "5000",
        )
    )

    # Runtime artifact root for VANTARIS ONE read-only resources.
    VANTARIS_ONE_ARTIFACT_ROOT = _env_str("VANTARIS_ONE_ARTIFACT_ROOT", "")
