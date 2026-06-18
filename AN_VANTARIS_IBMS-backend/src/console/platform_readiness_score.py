"""Platform readiness score derived from local registry."""

from __future__ import annotations

from typing import Any, Dict, List


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _clamp_score(value: float) -> float:
    return max(0.0, min(value, 100.0))


def _score_band(overall_score: float) -> str:
    if overall_score <= 24:
        return "early-foundation"
    if overall_score <= 49:
        return "foundation"
    if overall_score <= 74:
        return "readiness-candidate"
    return "operational-candidate"


def _module_readiness_score(modules: List[Dict[str, Any]]) -> float:
    status_base = {
        "ready": 78.0,
        "foundation": 56.0,
        "planned": 28.0,
        "not-integrated": 14.0,
    }
    readiness_bonus = {
        "readiness-candidate": 6.0,
        "r2-foundation": 4.0,
        "planned-runtime": 1.0,
        "external-foundation-reference": -2.0,
    }
    values: List[float] = []
    for item in modules:
        base = status_base.get(str(item.get("runtimeStatus", "planned")), 22.0)
        bonus = readiness_bonus.get(str(item.get("readinessLevel", "")), 0.0)
        capability = 0.0
        if bool(item.get("frontendReady")):
            capability += 4.0
        if bool(item.get("backendReady")):
            capability += 4.0
        if bool(item.get("apiReady")):
            capability += 4.0
        values.append(_clamp_score(base + bonus + capability))
    if not values:
        return 0.0
    return _clamp_score(sum(values) / len(values))


def _audit_readiness_score(modules: List[Dict[str, Any]]) -> float:
    value_map = {
        "ready": 70.0,
        "foundation": 52.0,
        "limited": 44.0,
        "planned": 20.0,
        "not-integrated": 8.0,
    }
    values = [value_map.get(str(item.get("auditReadiness", "planned")), 18.0) for item in modules]
    if not values:
        return 0.0
    return _clamp_score(sum(values) / len(values))


def _security_posture_score(modules: List[Dict[str, Any]]) -> float:
    values: List[float] = []
    for item in modules:
        score = 48.0
        flags = item.get("securityFlags", {})
        permission_mode = str(item.get("permissionMode", "not-integrated"))
        if permission_mode == "placeholder-allow":
            score -= 14.0
        elif permission_mode == "not-integrated":
            score -= 18.0
        if not bool(flags.get("realRbacIntegrated", False)):
            score -= 10.0
        if not bool(flags.get("siemIntegrated", False)):
            score -= 6.0
        if not bool(flags.get("ucdeRuntimeIntegrated", False)):
            score -= 5.0
        values.append(_clamp_score(score))
    if not values:
        return 0.0
    return _clamp_score(sum(values) / len(values))


def _integration_readiness_score(modules: List[Dict[str, Any]]) -> float:
    mode_base = {
        "local-skeleton": 54.0,
        "foundation-reference-only": 12.0,
        "not-integrated": 14.0,
    }
    values: List[float] = []
    for item in modules:
        mode = str(item.get("integrationMode", "not-integrated"))
        score = mode_base.get(mode, 18.0)
        flags = item.get("securityFlags", {})
        if bool(flags.get("edgeRuntimeIntegrated", False)):
            score += 10.0
        if bool(flags.get("linkRuntimeIntegrated", False)):
            score += 10.0
        values.append(_clamp_score(score))
    if not values:
        return 0.0
    return _clamp_score(sum(values) / len(values))


def calculate_platform_readiness_score(modules: List[Dict[str, Any]]) -> Dict[str, Any]:
    module_readiness = _module_readiness_score(modules)
    audit_readiness = _audit_readiness_score(modules)
    security_posture = _security_posture_score(modules)
    integration_readiness = _integration_readiness_score(modules)

    weighted = (
        module_readiness * 0.35
        + audit_readiness * 0.25
        + security_posture * 0.25
        + integration_readiness * 0.15
    )
    overall_score = round(_clamp_score(weighted), 2)

    return {
        "overallScore": overall_score,
        "scoreBand": _score_band(overall_score),
        "scoreMode": "registry-derived",
        "certified": False,
        "iec62443Certified": False,
        "components": {
            "moduleReadiness": {
                "score": round(module_readiness, 2),
                "weight": 0.35,
                "basis": "runtimeStatus, readinessLevel, frontendReady, backendReady, apiReady",
            },
            "auditReadiness": {
                "score": round(audit_readiness, 2),
                "weight": 0.25,
                "basis": "auditReadiness, audit storage, audit verification placeholders",
            },
            "securityPosture": {
                "score": round(security_posture, 2),
                "weight": 0.25,
                "basis": "permission mode, certified flags, RBAC/SIEM/UCDE integration status",
            },
            "integrationReadiness": {
                "score": round(integration_readiness, 2),
                "weight": 0.15,
                "basis": "integrationMode, edge/link runtime integration status",
            },
        },
        "drivers": [
            "Reports is at readiness-candidate level.",
            "UConsole module readiness registry foundation is available.",
            "Reports audit foundation is available.",
        ],
        "risks": [
            "Production RBAC is not integrated.",
            "EDGE and LINK runtime integration is not integrated.",
            "UCDE runtime evidence integration is not integrated.",
            "Most modules are still in planned stage.",
        ],
        "recommendations": [
            "Continue UConsole navigation and module health hardening.",
            "Build UCDE or Assets foundation in the next iteration.",
            "Keep certification claims disabled until formal validation is completed.",
        ],
    }

