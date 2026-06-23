"""CODE Policy Gate read-only preview API."""

from __future__ import annotations

from src.api import api_bp
from src.code_policy.code_policy_service import CodePolicyService
from src.common.models.response import Result


_service = CodePolicyService()


@api_bp.route("/v1/one/code-policy/health", methods=["GET"])
def code_policy_health():
    return Result.success(data=_service.health())


@api_bp.route("/v1/one/code-policy/summary", methods=["GET"])
def code_policy_summary():
    return Result.success(data=_service.summary())


@api_bp.route("/v1/one/code-policy/policy-gates", methods=["GET"])
def code_policy_policy_gates():
    return Result.success(data=_service.policy_gates())


@api_bp.route("/v1/one/code-policy/execution-boundary", methods=["GET"])
def code_policy_execution_boundary():
    return Result.success(data=_service.execution_boundary())


@api_bp.route("/v1/one/code-policy/approval-boundary", methods=["GET"])
def code_policy_approval_boundary():
    return Result.success(data=_service.approval_boundary())


@api_bp.route("/v1/one/code-policy/evidence-linkage", methods=["GET"])
def code_policy_evidence_linkage():
    return Result.success(data=_service.evidence_linkage())


@api_bp.route("/v1/one/code-policy/control-path", methods=["GET"])
def code_policy_control_path():
    return Result.success(data=_service.control_path())


@api_bp.route("/v1/one/code-policy/guardrails", methods=["GET"])
def code_policy_guardrails():
    return Result.success(data=_service.guardrails())

