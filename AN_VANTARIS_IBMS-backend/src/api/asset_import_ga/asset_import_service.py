"""Service facade for the production Asset Import Quality Gate skeleton."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any
import uuid

from src.api.asset_import_ga.asset_import_quality import (
    build_quality_report,
    combined_source_hash,
    now_iso,
    parse_workbook,
)
from src.api.asset_import_ga.asset_import_store import AssetImportRuntimeStore


PLATFORM = "VANTARIS ONE"
SCOPE = "ONE_AIRPORT_DATA_ASSET_MAP_GA_R2B"


@dataclass(frozen=True)
class UploadFile:
    source_file_name: str
    payload: bytes


def readonly_flags() -> dict[str, Any]:
    return {
        "platform": PLATFORM,
        "readOnly": True,
        "productionActivation": False,
        "runtimeActivation": False,
        "databaseAccess": False,
        "dbWrite": False,
        "approvalExecution": False,
    }


class AssetImportService:
    def __init__(self, store: AssetImportRuntimeStore | None = None) -> None:
        self.store = store or AssetImportRuntimeStore()

    def preview_upload(self, files: list[UploadFile]) -> dict[str, Any]:
        if not files:
            raise ValueError("file is required")
        for file in files:
            if not file.source_file_name.lower().endswith(".xlsx"):
                raise ValueError("Only .xlsx asset workbooks are supported.")

        import_batch_id = f"asset-import-{uuid.uuid4().hex[:16]}"
        uploaded_at = now_iso()
        validated_at = now_iso()
        all_records: list[dict[str, Any]] = []
        profiles: list[dict[str, Any]] = []
        for file in files:
            records, profile = parse_workbook(file.source_file_name, file.payload)
            all_records.extend(records)
            profiles.append(profile)
        source_file_name = " + ".join(profile["file_name"] for profile in profiles)
        source_file_hash = combined_source_hash(profile["file_hash_sha256"] for profile in profiles)
        report = build_quality_report(
            import_batch_id=import_batch_id,
            source_file_name=source_file_name,
            source_file_hash=source_file_hash,
            uploaded_at=uploaded_at,
            validated_at=validated_at,
            source_file_profiles=profiles,
            records=all_records,
        )
        summary = report["summary"]
        batch = {
            "scope": SCOPE,
            "import_batch_id": import_batch_id,
            "source_file_name": source_file_name,
            "source_file_hash": source_file_hash,
            "uploaded_at": uploaded_at,
            "validated_at": validated_at,
            "confirmed_at": None,
            "import_status": "preview_ready",
            "rollback_reference": f"dry-run-only:{import_batch_id}",
            "summary": summary,
            "alert": report["alert"],
            "quality_report": report,
            "dry_run_result": None,
        }
        self.store.create_batch(batch)
        return {
            **readonly_flags(),
            "batchId": import_batch_id,
            "summary": summary,
            "alert": report["alert"],
            "reportPreview": {
                "report_id": report["report_id"],
                "source_file_name": source_file_name,
                "source_file_hash": source_file_hash,
                "total_records": summary["total_records"],
                "readiness": summary["readiness"],
                "blocker_count": summary["blocker_count"],
                "major_count": summary["major_count"],
                "warning_count": summary["warning_count"],
                "info_count": summary["info_count"],
                "top_issues": report["issues"][:10],
            },
        }

    def list_batches(self) -> dict[str, Any]:
        return {**readonly_flags(), "batches": self.store.list_batches()}

    def get_report(self, batch_id: str) -> dict[str, Any] | None:
        batch = self.store.get_batch(batch_id)
        if not batch:
            return None
        return {**readonly_flags(), "report": batch["quality_report"]}

    def confirm(self, batch_id: str, confirmation: dict[str, Any] | None) -> tuple[dict[str, Any] | None, int, str]:
        batch = self.store.get_batch(batch_id)
        if not batch:
            return None, 404, "batch not found"

        summary = batch["summary"]
        if int(summary.get("blocker_count", 0)) > 0:
            return None, 409, "Import blocked until critical issues are resolved."

        if int(summary.get("major_count", 0)) > 0 or int(summary.get("warning_count", 0)) > 0:
            confirmation = confirmation or {}
            if confirmation.get("reviewed_quality_report") is not True or confirmation.get("accepted_unresolved_warnings") is not True:
                return None, 400, "reviewed_quality_report and accepted_unresolved_warnings are required."

        confirmed_at = now_iso()
        skipped_records = int(summary.get("blocker_count", 0)) + int(summary.get("major_count", 0))
        created_assets_estimate = max(int(summary.get("total_records", 0)) - skipped_records, 0)
        dry_run = {
            "import_status": "confirmed_dry_run",
            "created_assets_estimate": created_assets_estimate,
            "updated_assets_estimate": 0,
            "skipped_records": skipped_records,
            "audit_summary": {
                "import_batch_id": batch_id,
                "source_file_name": batch.get("source_file_name", ""),
                "source_file_hash": batch.get("source_file_hash", ""),
                "confirmed_at": confirmed_at,
                "readiness": summary.get("readiness", ""),
                "blocker_count": summary.get("blocker_count", 0),
                "major_count": summary.get("major_count", 0),
                "warning_count": summary.get("warning_count", 0),
                "registry_write": False,
                "dry_run_only": True,
            },
        }
        updated = deepcopy(batch)
        updated["confirmed_at"] = confirmed_at
        updated["import_status"] = "confirmed_dry_run"
        updated["dry_run_result"] = dry_run
        self.store.save_batch(updated)
        return {**readonly_flags(), **dry_run}, 200, "success"

    def audit(self, batch_id: str) -> dict[str, Any] | None:
        batch = self.store.get_batch(batch_id)
        if not batch:
            return None
        summary = batch.get("summary", {})
        return {
            **readonly_flags(),
            "audit": {
                "import_batch_id": batch.get("import_batch_id", ""),
                "source_file_name": batch.get("source_file_name", ""),
                "source_file_hash": batch.get("source_file_hash", ""),
                "uploaded_at": batch.get("uploaded_at", ""),
                "validated_at": batch.get("validated_at", ""),
                "confirmed_at": batch.get("confirmed_at"),
                "total_records": summary.get("total_records", 0),
                "blocker_count": summary.get("blocker_count", 0),
                "major_count": summary.get("major_count", 0),
                "warning_count": summary.get("warning_count", 0),
                "info_count": summary.get("info_count", 0),
                "readiness": summary.get("readiness", ""),
                "import_status": batch.get("import_status", "preview_ready"),
                "rollback_reference": batch.get("rollback_reference", ""),
            },
        }
