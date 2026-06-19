"""Bounded multi-site reconciliation context for evidence packages."""
from __future__ import annotations

from dataclasses import replace
from typing import Any, Mapping, Optional, Sequence

from src.asset_graph.compatibility.models import ProjectionContext

SINGLE_SITE_STRICT = "SINGLE_SITE_STRICT"
MULTI_SITE_DECLARED = "MULTI_SITE_DECLARED"
SUPPORTED_MODES = frozenset({SINGLE_SITE_STRICT, MULTI_SITE_DECLARED})
UNSUPPORTED_MODES = frozenset({"ALL_SITES", "ANY_SITE", "UNRESTRICTED"})
MAX_ALLOWED_SITES = 100
WILDCARD_MARKERS = ("*", "?", "%")


class SiteContextError(ValueError):
    """Invalid evidence package site context."""


def _clean_id(value: Any, label: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise SiteContextError(f"{label} is required")
    if any(marker in text for marker in WILDCARD_MARKERS):
        raise SiteContextError(f"{label} contains unsupported wildcard characters")
    return text


def _normalize_allowed_site_ids(values: Any) -> tuple[str, ...]:
    if not isinstance(values, (list, tuple)):
        raise SiteContextError("allowedSiteIds must be a list")
    if not values:
        raise SiteContextError("allowedSiteIds must not be empty")
    if len(values) > MAX_ALLOWED_SITES:
        raise SiteContextError("allowedSiteIds exceeds maximum allowed sites")
    normalized: list[str] = []
    seen: set[str] = set()
    for item in values:
        site_id = _clean_id(item, "allowedSiteId")
        if site_id in seen:
            raise SiteContextError("allowedSiteIds must be unique")
        seen.add(site_id)
        normalized.append(site_id)
    return tuple(sorted(normalized))


def parse_site_context(site_context: Mapping[str, Any], *, tenant_id: str) -> ProjectionContext:
    del tenant_id  # tenant/site binding is enforced at record level; sites are tenant-scoped by policy
    if not isinstance(site_context, Mapping):
        raise SiteContextError("siteContext must be an object")

    mode_raw = site_context.get("mode")
    site_id_raw = site_context.get("siteId")
    primary_raw = site_context.get("primarySiteId")
    allowed_raw = site_context.get("allowedSiteIds")

    if mode_raw is None and site_id_raw:
        mode = SINGLE_SITE_STRICT
        primary_site_id = _clean_id(site_id_raw, "siteId")
        allowed_site_ids: tuple[str, ...] = (primary_site_id,)
        context_site_id = primary_site_id
    elif str(mode_raw or "").strip().upper() in UNSUPPORTED_MODES:
        raise SiteContextError("unsupported site context mode")
    elif str(mode_raw or "").strip() == MULTI_SITE_DECLARED:
        mode = MULTI_SITE_DECLARED
        primary_site_id = _clean_id(primary_raw, "primarySiteId")
        allowed_site_ids = _normalize_allowed_site_ids(allowed_raw)
        if primary_site_id not in allowed_site_ids:
            raise SiteContextError("primarySiteId must belong to allowedSiteIds")
        context_site_id = primary_site_id
    elif mode_raw in (None, "", SINGLE_SITE_STRICT):
        mode = SINGLE_SITE_STRICT
        primary_site_id = _clean_id(site_id_raw or primary_raw, "siteId")
        allowed_site_ids = (primary_site_id,)
        context_site_id = primary_site_id
    else:
        raise SiteContextError("unsupported site context mode")

    if mode not in SUPPORTED_MODES:
        raise SiteContextError("unsupported site context mode")

    return ProjectionContext(
        tenant_id="",  # filled by caller
        source_system_id="",
        source_namespace="",
        site_id=context_site_id,
        site_scope_mode=mode,
        primary_site_id=primary_site_id,
        allowed_site_ids=allowed_site_ids,
    )


def merge_site_context(base: ProjectionContext, **fields: Any) -> ProjectionContext:
    return replace(base, **fields)


def allows_record_site(context: ProjectionContext, record_site_id: Optional[str]) -> bool:
    if record_site_id is None or not str(record_site_id).strip():
        return True
    record_site = str(record_site_id).strip()
    if context.site_scope_mode == MULTI_SITE_DECLARED:
        return record_site in context.allowed_site_ids
    declared_site = context.site_id or context.primary_site_id
    if declared_site:
        return record_site == declared_site
    return True


def collect_scope_metrics(
    context: ProjectionContext,
    devices_raw: Sequence[Mapping[str, Any]],
    validation_blockers: Sequence[Mapping[str, str]],
    record_results: Sequence[Any],
) -> dict[str, Any]:
    in_scope = 0
    outside_scope = 0
    single_site_mismatch = 0
    multi_site_undeclared = 0
    tenant_mismatch = 0
    site_pass = 0
    site_blocker = 0

    for raw in devices_raw:
        site = str(raw.get("siteId", "")).strip() if isinstance(raw, Mapping) else ""
        if site and allows_record_site(context, site):
            in_scope += 1
        elif site:
            outside_scope += 1

    for item in validation_blockers:
        code = str(item.get("code", ""))
        if code == "TENANT_SCOPE_MISMATCH":
            tenant_mismatch += 1
        if code == "SITE_SCOPE_MISMATCH":
            site_blocker += 1
            if context.site_scope_mode == SINGLE_SITE_STRICT:
                single_site_mismatch += 1
            else:
                multi_site_undeclared += 1

    for record in record_results:
        if record.canonical_global_id:
            site_pass += 1
        elif any("SITE" in blocker for blocker in record.cutover_blockers):
            site_blocker += 1

    return {
        "scopeMode": context.site_scope_mode,
        "primarySiteIdDeclared": context.primary_site_id or context.site_id,
        "allowedSiteCount": len(context.allowed_site_ids),
        "recordsInDeclaredSiteScope": in_scope,
        "recordsOutsideDeclaredSiteScope": outside_scope,
        "singleSiteMismatchCount": single_site_mismatch,
        "multiSiteUndeclaredSiteCount": multi_site_undeclared,
        "tenantMismatchCount": tenant_mismatch,
        "siteScopePassCount": site_pass,
        "siteScopeBlockerCount": site_blocker,
    }
