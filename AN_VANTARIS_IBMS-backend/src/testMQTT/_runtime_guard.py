"""Production guard for standalone testMQTT / simulator entry points (SECURITY-A8)."""
import os
import sys

_TRUE = frozenset({"1", "true", "yes", "on"})


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None or not str(value).strip():
        return default
    return str(value).strip().lower() in _TRUE


def is_production() -> bool:
    return os.getenv("IBMS_ENV", "development").strip().lower() == "production"


def require_testmqtt_enabled(component: str) -> None:
    """Block testMQTT scripts in production; require explicit enable in non-production."""
    if is_production():
        print(
            f"[SECURITY-A8] {component}: blocked in production (IBMS_ENV=production). "
            "testMQTT must not run in production."
        )
        sys.exit(1)
    if not _env_bool("IBMS_TESTMQTT_ENABLED", False):
        print(
            f"[SECURITY-A8] {component}: IBMS_TESTMQTT_ENABLED is not true. "
            "Set IBMS_TESTMQTT_ENABLED=true to run in non-production."
        )
        sys.exit(0)


def require_simulator_enabled(component: str) -> None:
    """Block standalone simulators / mock servers in production."""
    if is_production():
        print(
            f"[SECURITY-A8] {component}: blocked in production (IBMS_ENV=production). "
            "Simulators must not run in production."
        )
        sys.exit(1)
    if not _env_bool("IBMS_SIMULATOR_ENABLED", False):
        print(
            f"[SECURITY-A8] {component}: IBMS_SIMULATOR_ENABLED is not true. "
            "Set IBMS_SIMULATOR_ENABLED=true to run in non-production."
        )
        sys.exit(0)
