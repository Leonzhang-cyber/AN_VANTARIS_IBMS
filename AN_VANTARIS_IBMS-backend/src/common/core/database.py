# src/common/core/database.py
from flask_sqlalchemy import SQLAlchemy

try:
    from src.common.config.default import Config as AppConfig
except ImportError:
    raise RuntimeError("❌ 无法导入配置类：src.config.default.Config，请检查项目路径。")

db = SQLAlchemy()


def resolve_database_uri(config=None) -> str:
    """
    Resolve SQLAlchemy database URI from configuration.

    Priority:
    1. Config.SQLALCHEMY_DATABASE_URI (from IBMS_DATABASE_URL or normalized URL)
    2. Legacy IBMS_DB_* component fallback (MySQL)
    """
    cfg = config or AppConfig
    uri = getattr(cfg, "SQLALCHEMY_DATABASE_URI", None)
    if uri and str(uri).strip():
        return str(uri).strip()

    return (
        f"mysql+pymysql://{cfg.DB_USER}:{cfg.DB_PASSWORD}"
        f"@{cfg.DB_HOST}:{cfg.DB_PORT}/{cfg.DB_NAME}"
    )


def init_database(app) -> None:
    """Initialize Flask-SQLAlchemy using the resolved database URI (no connection test)."""
    uri = app.config.get("SQLALCHEMY_DATABASE_URI") or resolve_database_uri()
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
