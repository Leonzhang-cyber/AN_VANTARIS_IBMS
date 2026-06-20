"""Validation helpers for read-only Operations Console Packages."""
from __future__ import annotations

from typing import Any, Mapping

from .errors import OperationsConsolePackageError


def validate_operations_console_package(package: Mapping[str, Any]) -> None:
    summary = package.get("summary", {})
    if len(package.get("pageDefinitions", [])) != 8 or summary.get("pageDefinitionCount") != 8:
        raise OperationsConsolePackageError("PAGE_DEFINITION_COUNT_INVALID", "expected eight page definitions")
    if len(package.get("navigationGroups", [])) != 3 or summary.get("navigationGroupCount") != 3:
        raise OperationsConsolePackageError("NAVIGATION_GROUP_COUNT_INVALID", "expected three navigation groups")
    if len(package.get("consoleCards", [])) != 8 or summary.get("consoleCardCount") != 8:
        raise OperationsConsolePackageError("CONSOLE_CARD_COUNT_INVALID", "expected eight console cards")
    if len(package.get("packageDataSources", [])) != 15 or summary.get("packageDataSourceCount") != 15:
        raise OperationsConsolePackageError("DATA_SOURCE_COUNT_INVALID", "expected fifteen package data sources")
    if len(package.get("packageReadinessGates", [])) != 12 or summary.get("packageReadinessGateCount") != 12:
        raise OperationsConsolePackageError("GATE_COUNT_INVALID", "expected twelve readiness gates")
    for data_source in package.get("packageDataSources", []):
        for key, expected in (("readOnly", True), ("apiEnabled", False), ("frontendEnabled", False), ("databaseAccessEnabled", False)):
            if data_source.get(key) is not expected:
                raise OperationsConsolePackageError("DATA_SOURCE_BOUNDARY_INVALID", f"{data_source.get('dataSourceKey')} {key} invalid")
    for key in (
        "runtimeObservedCount",
        "runtimeAlarmObservedCount",
        "ufmsFaultCaseCreatedCount",
        "workOrderIntentCreatedCount",
        "workOrderCreatedCount",
        "evidenceCenterWriteCount",
        "ummsWriteCount",
        "oneWorkManagementWriteCount",
        "decisionWriteCount",
        "approvalWriteCount",
        "auditWriteCount",
        "canonicalWriteCount",
        "databaseWriteCount",
    ):
        if summary.get(key) != 0:
            raise OperationsConsolePackageError("FORBIDDEN_WRITE_OR_RUNTIME_COUNT", f"{key} must be zero")
    for key in ("apiEnabled", "frontendEnabled", "runtimeActivationAllowed", "productionActivationAllowed", "pushAllowed", "containsCustomerAssetIdentifiers", "airportSpecific"):
        if summary.get(key) is not False:
            raise OperationsConsolePackageError("FORBIDDEN_CAPABILITY_ENABLED", f"{key} must be false")
    if summary.get("crossIndustry") is not True:
        raise OperationsConsolePackageError("CROSS_INDUSTRY_INVALID", "VANTARIS ONE package model must remain cross-industry")
    if any(gate.get("blocking") and gate.get("status") != "PASS" for gate in package.get("packageReadinessGates", [])):
        raise OperationsConsolePackageError("BLOCKING_GATE_FAILED", "all blocking gates must pass")


def validate_boundary(source_text: str) -> None:
    lowered = source_text.lower()
    forbidden = ("sql" + "alchemy", "fla" + "sk", "req" + "uests.", "url" + "lib", "soc" + "ket", "blue" + "print", "rea" + "ct", "src." + "ufms", "src." + "umms")
    found = [token for token in forbidden if token in lowered]
    if found:
        raise OperationsConsolePackageError("BOUNDARY_VIOLATION", ", ".join(found))
