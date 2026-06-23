"""Customer Delivery read-only preview API."""

from __future__ import annotations

from src.api import api_bp
from src.common.models.response import Result
from src.customer_delivery.readonly_preview_provider import (
    checklist,
    customer_delivery_preview,
    guardrails,
    package_readiness,
    r2_customer_handoff_checklist,
    r2_engineer_readiness_checklist,
    r2_export_scope,
    r2_handoff_decision,
    r2_offline_readiness,
    server_plan,
)


@api_bp.route("/one/customer-delivery/preview", methods=["GET"])
def customer_delivery_preview_route():
    return Result.success(data=customer_delivery_preview())


@api_bp.route("/one/customer-delivery/offline-package", methods=["GET"])
def customer_delivery_offline_package_route():
    return Result.success(data=checklist("offlinePackage"))


@api_bp.route("/one/customer-delivery/precheck", methods=["GET"])
def customer_delivery_precheck_route():
    return Result.success(data=checklist("precheck"))


@api_bp.route("/one/customer-delivery/installation-plan", methods=["GET"])
def customer_delivery_installation_plan_route():
    return Result.success(data=checklist("installationPlan"))


@api_bp.route("/one/customer-delivery/verification-plan", methods=["GET"])
def customer_delivery_verification_plan_route():
    return Result.success(data=checklist("verificationPlan"))


@api_bp.route("/one/customer-delivery/rollback-plan", methods=["GET"])
def customer_delivery_rollback_plan_route():
    return Result.success(data=checklist("rollbackPlan"))


@api_bp.route("/one/customer-delivery/acceptance-checklist", methods=["GET"])
def customer_delivery_acceptance_checklist_route():
    return Result.success(data=checklist("acceptanceChecklist"))


@api_bp.route("/one/customer-delivery/server-plan", methods=["GET"])
def customer_delivery_server_plan_route():
    return Result.success(data=server_plan())


@api_bp.route("/one/customer-delivery/guardrails", methods=["GET"])
def customer_delivery_guardrails_route():
    return Result.success(data=guardrails())


@api_bp.route("/one/customer-delivery/offline-readiness", methods=["GET"])
def customer_delivery_r2_offline_readiness_route():
    return Result.success(data=r2_offline_readiness())


@api_bp.route("/one/customer-delivery/handoff-decision", methods=["GET"])
def customer_delivery_r2_handoff_decision_route():
    return Result.success(data=r2_handoff_decision())


@api_bp.route("/one/customer-delivery/package-readiness-matrix", methods=["GET"])
def customer_delivery_r2_package_readiness_matrix_route():
    return Result.success(data=r2_offline_readiness())


@api_bp.route("/one/customer-delivery/export-scope", methods=["GET"])
def customer_delivery_r2_export_scope_route():
    return Result.success(data=r2_export_scope())


@api_bp.route("/one/customer-delivery/server-handoff-plan", methods=["GET"])
def customer_delivery_r2_server_handoff_plan_route():
    return Result.success(data=server_plan())


@api_bp.route("/one/customer-delivery/customer-handoff-checklist", methods=["GET"])
def customer_delivery_r2_customer_handoff_checklist_route():
    return Result.success(data=r2_customer_handoff_checklist())


@api_bp.route("/one/customer-delivery/engineer-readiness-checklist", methods=["GET"])
def customer_delivery_r2_engineer_readiness_checklist_route():
    return Result.success(data=r2_engineer_readiness_checklist())
