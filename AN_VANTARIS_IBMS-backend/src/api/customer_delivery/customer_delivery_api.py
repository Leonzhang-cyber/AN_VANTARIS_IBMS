"""Customer Delivery read-only preview API."""

from __future__ import annotations

from src.api import api_bp
from src.common.models.response import Result
from src.customer_delivery.readonly_preview_provider import (
    checklist,
    customer_delivery_preview,
    guardrails,
    package_readiness,
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

