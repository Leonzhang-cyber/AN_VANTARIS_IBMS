"""NexusAI read-only branch audit API."""

from __future__ import annotations

from src.api import api_bp
from src.common.models.response import Result
from src.nexus_ai.nexus_branch_audit_service import NexusBranchAuditService


_service = NexusBranchAuditService()


@api_bp.route("/v1/one/nexus-ai/health", methods=["GET"])
def nexus_ai_health():
    return Result.success(data=_service.health())


@api_bp.route("/v1/one/nexus-ai/branch-audit/summary", methods=["GET"])
def nexus_ai_branch_audit_summary():
    return Result.success(data=_service.summary())


@api_bp.route("/v1/one/nexus-ai/branch-audit/commits", methods=["GET"])
def nexus_ai_branch_audit_commits():
    return Result.success(data=_service.commits())


@api_bp.route("/v1/one/nexus-ai/branch-audit/modules", methods=["GET"])
def nexus_ai_branch_audit_modules():
    return Result.success(data=_service.modules())


@api_bp.route("/v1/one/nexus-ai/branch-audit/risks", methods=["GET"])
def nexus_ai_branch_audit_risks():
    return Result.success(data=_service.risks())


@api_bp.route("/v1/one/nexus-ai/branch-audit/evidence-linkage", methods=["GET"])
def nexus_ai_branch_audit_evidence_linkage():
    return Result.success(data=_service.evidence_linkage())


@api_bp.route("/v1/one/nexus-ai/branch-audit/customer-demo-impact", methods=["GET"])
def nexus_ai_branch_audit_customer_demo_impact():
    return Result.success(data=_service.customer_demo_impact())


@api_bp.route("/v1/one/nexus-ai/branch-audit/guardrails", methods=["GET"])
def nexus_ai_branch_audit_guardrails():
    return Result.success(data=_service.guardrails())

