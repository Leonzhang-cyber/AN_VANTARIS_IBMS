"""Validation helpers for read-only frontend page contracts."""
from __future__ import annotations

from typing import Any, Mapping

from .errors import ReadOnlyFrontendPageContractError


EXPECTED_SUMMARY = {
    "pageContractCount": 8,
    "layoutContractCount": 8,
    "componentBindingContractCount": 24,
    "uiStateContractCount": 48,
    "interactionContractCount": 64,
    "localSmokeCaseCount": 8,
    "smokeGateCount": 16,
    "passedSmokeGateCount": 16,
    "blockingGateFailureCount": 0,
    "staticOnlyPageCount": 8,
    "readOnlyPageCount": 8,
    "productionEnabledPageCount": 0,
    "liveApiCallEnabledPageCount": 0,
    "dataMutationEnabledPageCount": 0,
    "liveApiCallEnabledComponentCount": 0,
    "dataMutationEnabledComponentCount": 0,
    "mutationAllowedInteractionCount": 0,
    "browserLaunchRequiredCount": 0,
    "networkCallRequiredCount": 0,
    "localhostCallRequiredCount": 0,
    "productionRouteEnabledCount": 0,
    "a8FrontendSkeletonPageCount": 8,
    "a7ReadOnlyApiRouteImplementationAllowed": True,
    "frontendEnabled": False,
    "apiEnabled": False,
    "databaseWriteCount": 0,
    "canonicalWriteCount": 0,
    "decisionWriteCount": 0,
    "approvalWriteCount": 0,
    "auditWriteCount": 0,
    "runtimeActivationAllowed": False,
    "productionActivationAllowed": False,
    "pushAllowed": False,
    "containsCustomerAssetIdentifiers": False,
    "crossIndustry": True,
    "airportSpecific": False,
}


def validate_read_only_frontend_page_contract(contract: Mapping[str, Any]) -> None:
    summary = contract.get("summary", {})
    for key, value in EXPECTED_SUMMARY.items():
        if summary.get(key) != value:
            raise ReadOnlyFrontendPageContractError("SUMMARY_INVALID", f"{key} must be {value}")
    for name, count in (
        ("pageContracts", 8),
        ("layoutContracts", 8),
        ("componentBindingContracts", 24),
        ("uiStateContracts", 48),
        ("interactionContracts", 64),
        ("localSmokeCases", 8),
        ("smokeGateResults", 16),
    ):
        if len(contract.get(name, [])) != count:
            raise ReadOnlyFrontendPageContractError("COUNT_INVALID", f"{name} must contain {count}")
    for page in contract.get("pageContracts", []):
        if page.get("staticOnly") is not True or page.get("readOnly") is not True:
            raise ReadOnlyFrontendPageContractError("PAGE_BOUNDARY_INVALID", "pages must be static and read-only")
        for key in ("productionEnabled", "liveApiCallEnabled", "dataMutationEnabled"):
            if page.get(key) is not False:
                raise ReadOnlyFrontendPageContractError("PAGE_BOUNDARY_INVALID", f"{key} must be false")
    for binding in contract.get("componentBindingContracts", []):
        if binding.get("readOnly") is not True or binding.get("liveApiCallEnabled") is not False or binding.get("dataMutationEnabled") is not False:
            raise ReadOnlyFrontendPageContractError("COMPONENT_BOUNDARY_INVALID", "component bindings must be read-only without live API or mutation")
    if any(item.get("mutationAllowed") is not False or item.get("readOnly") is not True for item in contract.get("interactionContracts", [])):
        raise ReadOnlyFrontendPageContractError("INTERACTION_BOUNDARY_INVALID", "interactions must be read-only and non-mutating")
    if any(item.get("browserLaunchRequired") is not False or item.get("networkCallRequired") is not False or item.get("localhostCallRequired") is not False for item in contract.get("localSmokeCases", [])):
        raise ReadOnlyFrontendPageContractError("SMOKE_BOUNDARY_INVALID", "local smoke cases must not require browser/network/localhost")
    if any(gate.get("status") != "PASS" for gate in contract.get("smokeGateResults", [])):
        raise ReadOnlyFrontendPageContractError("GATE_STATUS_INVALID", "all smoke gates must pass")


def validate_boundary(source_text: str) -> None:
    lowered = source_text.lower()
    forbidden = (
        "sql" + "alchemy",
        "fla" + "sk",
        "fast" + "api",
        "req" + "uests.",
        "url" + "lib",
        "soc" + "ket",
        "src." + "ufms",
        "src." + "umms",
        "rea" + "ct",
        "v" + "ue",
    )
    found = [token for token in forbidden if token in lowered]
    if found:
        raise ReadOnlyFrontendPageContractError("BOUNDARY_VIOLATION", ", ".join(found))
