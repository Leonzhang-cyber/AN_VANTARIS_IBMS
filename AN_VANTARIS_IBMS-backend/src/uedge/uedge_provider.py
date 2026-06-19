"""UEDGE local provider (read-only setup and diagnostics skeleton)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_uedge_health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "moduleId": "uedge",
        "moduleName": "UEDGE Setup & Diagnostics",
        "runtimeMode": "local-skeleton",
        "provider": "local-uedge-provider",
        "readOnly": True,
        "controlActionsEnabled": False,
        "runtimeLinked": False,
        "edgeRuntimeIntegrated": False,
        "linkRuntimeIntegrated": False,
        "certified": False,
        "iec62443Certified": False,
    }


def get_customer_setup() -> Dict[str, Any]:
    return {
        "setupMode": "local-skeleton-setup",
        "customerSetupReady": True,
        "oneClickSetupEnabled": False,
        "realDeviceRegistrationEnabled": False,
        "certificateImportEnabled": False,
        "tokenProvisioningEnabled": False,
        "networkConfigEnabled": False,
        "runtimeLinked": False,
        "edgeRuntimeIntegrated": False,
        "linkRuntimeIntegrated": False,
        "readOnly": True,
        "controlActionsEnabled": False,
        "certified": False,
        "iec62443Certified": False,
        "lastUpdated": _now_iso(),
    }


def get_setup_steps() -> List[Dict[str, Any]]:
    return [
        {
            "stepId": "select-site",
            "stepName": "Select site",
            "stepOrder": 1,
            "status": "ready",
            "required": True,
            "actionEnabled": False,
            "runtimeLinked": False,
            "notes": "Site selection is preview-only and does not write runtime configuration.",
        },
        {
            "stepId": "select-gateway-template",
            "stepName": "Select gateway template",
            "stepOrder": 2,
            "status": "placeholder",
            "required": True,
            "actionEnabled": False,
            "runtimeLinked": False,
            "notes": "Gateway templates are placeholders in this stage.",
        },
        {
            "stepId": "review-network-prerequisites",
            "stepName": "Review network prerequisites",
            "stepOrder": 3,
            "status": "placeholder",
            "required": True,
            "actionEnabled": False,
            "runtimeLinked": False,
            "notes": "Network requirements are displayed without writing network configuration.",
        },
        {
            "stepId": "review-certificate-token-placeholder",
            "stepName": "Review certificate/token placeholder",
            "stepOrder": 4,
            "status": "placeholder",
            "required": True,
            "actionEnabled": False,
            "runtimeLinked": False,
            "notes": "Certificate and token operations are disabled in local skeleton mode.",
        },
        {
            "stepId": "review-connector-template-placeholder",
            "stepName": "Review connector template placeholder",
            "stepOrder": 5,
            "status": "placeholder",
            "required": True,
            "actionEnabled": False,
            "runtimeLinked": False,
            "notes": "Connector and protocol templates are preview-only metadata.",
        },
        {
            "stepId": "confirm-dry-run-readiness",
            "stepName": "Confirm local dry-run readiness",
            "stepOrder": 6,
            "status": "ready",
            "required": True,
            "actionEnabled": False,
            "runtimeLinked": False,
            "notes": "Dry-run readiness confirms placeholder completeness only.",
        },
    ]


def get_engineer_diagnostics() -> Dict[str, Any]:
    return {
        "diagnosticsMode": "local-skeleton-diagnostics",
        "engineerDiagnosticsReady": True,
        "runtimeConnected": False,
        "connectorDiagnosticsEnabled": False,
        "protocolDiagnosticsEnabled": False,
        "mappingReviewEnabled": False,
        "bufferInspectionEnabled": False,
        "deliveryInspectionEnabled": False,
        "edgeRuntimeIntegrated": False,
        "linkRuntimeIntegrated": False,
        "runtimeLinked": False,
        "readOnly": True,
        "controlActionsEnabled": False,
        "certified": False,
        "iec62443Certified": False,
        "lastUpdated": _now_iso(),
    }


def get_diagnostics_panels() -> List[Dict[str, Any]]:
    return [
        {
            "panelId": "gateway-identity",
            "panelName": "Gateway Identity",
            "panelType": "identity",
            "status": "placeholder",
            "runtimeLinked": False,
            "actionEnabled": False,
            "summary": "Gateway identity fields are preview-only.",
            "limitations": ["No runtime identity retrieval.", "No registration workflow."],
        },
        {
            "panelId": "network-prerequisites",
            "panelName": "Network Prerequisites",
            "panelType": "network",
            "status": "placeholder",
            "runtimeLinked": False,
            "actionEnabled": False,
            "summary": "Network prerequisites checklist is read-only.",
            "limitations": ["No network probing.", "No network configuration changes."],
        },
        {
            "panelId": "connector-status",
            "panelName": "Connector Status Placeholder",
            "panelType": "connector",
            "status": "placeholder",
            "runtimeLinked": False,
            "actionEnabled": False,
            "summary": "Connector status is not connected to runtime.",
            "limitations": ["No connector lifecycle controls.", "No runtime connector check."],
        },
        {
            "panelId": "protocol-status",
            "panelName": "Protocol Status Placeholder",
            "panelType": "protocol",
            "status": "placeholder",
            "runtimeLinked": False,
            "actionEnabled": False,
            "summary": "Protocol status is local placeholder metadata.",
            "limitations": ["No Modbus/BACnet/SNMP/OPC probing.", "No protocol tests."],
        },
        {
            "panelId": "mapping-review",
            "panelName": "Mapping Review Placeholder",
            "panelType": "mapping",
            "status": "placeholder",
            "runtimeLinked": False,
            "actionEnabled": False,
            "summary": "Mapping review is local template preview.",
            "limitations": ["No runtime mapping sync.", "No mapping deploy."],
        },
        {
            "panelId": "buffer-status",
            "panelName": "Buffer Status Placeholder",
            "panelType": "buffer",
            "status": "placeholder",
            "runtimeLinked": False,
            "actionEnabled": False,
            "summary": "Buffer status is non-runtime placeholder.",
            "limitations": ["No runtime buffer inspection.", "No queue controls."],
        },
        {
            "panelId": "heartbeat-placeholder",
            "panelName": "Heartbeat Placeholder",
            "panelType": "heartbeat",
            "status": "placeholder",
            "runtimeLinked": False,
            "actionEnabled": False,
            "summary": "Heartbeat timeline is preview-only.",
            "limitations": ["No runtime heartbeat feed.", "No endpoint calls."],
        },
        {
            "panelId": "delivery-readiness",
            "panelName": "Delivery Readiness Placeholder",
            "panelType": "delivery",
            "status": "placeholder",
            "runtimeLinked": False,
            "actionEnabled": False,
            "summary": "Delivery readiness is static skeleton summary.",
            "limitations": ["No runtime delivery inspection.", "No forwarding operations."],
        },
    ]


def get_uedge_summary() -> Dict[str, Any]:
    setup = get_customer_setup()
    diagnostics = get_engineer_diagnostics()
    panels = get_diagnostics_panels()
    steps = get_setup_steps()
    return {
        "moduleId": "uedge",
        "moduleName": "UEDGE Setup & Diagnostics",
        "setupMode": setup.get("setupMode"),
        "diagnosticsMode": diagnostics.get("diagnosticsMode"),
        "customerSetupReady": bool(setup.get("customerSetupReady")),
        "engineerDiagnosticsReady": bool(diagnostics.get("engineerDiagnosticsReady")),
        "setupStepCount": len(steps),
        "diagnosticsPanelCount": len(panels),
        "oneClickSetupEnabled": bool(setup.get("oneClickSetupEnabled")),
        "runtimeConnected": bool(diagnostics.get("runtimeConnected")),
        "runtimeLinked": False,
        "readOnly": True,
        "controlActionsEnabled": False,
        "edgeRuntimeIntegrated": False,
        "linkRuntimeIntegrated": False,
        "certified": False,
        "iec62443Certified": False,
    }

