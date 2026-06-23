"""Asset Context service facade."""

from __future__ import annotations

from typing import Any, Dict, Optional

from src.asset_context.asset_context_provider import (
    get_asset_context,
    get_asset_links,
    get_graph,
    get_guardrails,
    get_health,
    get_summary,
    list_asset_contexts,
)


class AssetContextService:
    """Read-only facade for unified asset context projections."""

    def health(self) -> Dict[str, Any]:
        return get_health()

    def summary(self) -> Dict[str, Any]:
        return get_summary()

    def assets(self) -> Dict[str, Any]:
        return list_asset_contexts()

    def asset_detail(self, asset_id: str) -> Optional[Dict[str, Any]]:
        return get_asset_context(asset_id)

    def asset_links(self, asset_id: str) -> Optional[Dict[str, Any]]:
        return get_asset_links(asset_id)

    def graph(self) -> Dict[str, Any]:
        return get_graph()

    def guardrails(self) -> Dict[str, Any]:
        return get_guardrails()

