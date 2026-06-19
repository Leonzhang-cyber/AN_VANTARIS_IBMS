"""Tests for offline legacy device reconciliation evidence runner."""
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
RUNNER_SCRIPT = ROOT / "scripts/validation/run-one-device-reconciliation-evidence.py"
MODULE_FILE = ROOT / "AN_VANTARIS_IBMS-backend/src/asset_graph/reconciliation/evidence/runner.py"
SAMPLE_DIR = ROOT / "AN_VANTARIS_ONE/evidence/device-reconciliation/sample"


class TestDeviceReconciliationEvidenceRunner(unittest.TestCase):
    maxDiff = None

    def _run(self, sample: str, output: Path, run_id: str, extra: list[str] | None = None) -> subprocess.CompletedProcess[str]:
        command = [
            "python3",
            str(RUNNER_SCRIPT),
            "--root",
            str(ROOT),
            "--input",
            f"AN_VANTARIS_ONE/evidence/device-reconciliation/sample/{sample}",
            "--output",
            str(output),
            "--run-id",
            run_id,
            "--format",
            "json",
        ]
        if extra:
            command.extend(extra)
        return subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)

    def _load_json(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    # 1
    def test_valid_package_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "evidence.json"
            result = self._run("minimal-valid-device.json", output, "TEST-RUN-001")
            self.assertEqual(result.returncode, 0)
            self.assertTrue(output.is_file())

    # 2
    def test_invalid_format_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self._load_json(SAMPLE_DIR / "minimal-valid-device.json")
            package["formatName"] = "BAD"
            input_path = Path(directory) / "bad-format.json"
            input_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
            output = Path(directory) / "out.json"
            command = [
                "python3",
                str(RUNNER_SCRIPT),
                "--root",
                str(ROOT),
                "--input",
                str(input_path),
                "--output",
                str(output),
                "--run-id",
                "TEST-RUN-002",
                "--format",
                "json",
            ]
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertNotEqual(result.returncode, 0)

    # 3
    def test_unsupported_version_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self._load_json(SAMPLE_DIR / "minimal-valid-device.json")
            package["formatVersion"] = "9.9.9"
            input_path = Path(directory) / "bad-version.json"
            input_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
            output = Path(directory) / "out.json"
            result = subprocess.run(
                [
                    "python3", str(RUNNER_SCRIPT), "--root", str(ROOT), "--input", str(input_path),
                    "--output", str(output), "--run-id", "TEST-RUN-003", "--format", "json",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)

    # 4
    def test_missing_tenant_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self._load_json(SAMPLE_DIR / "minimal-valid-device.json")
            package["tenantContext"] = {}
            input_path = Path(directory) / "missing-tenant.json"
            input_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
            output = Path(directory) / "out.json"
            result = subprocess.run(
                ["python3", str(RUNNER_SCRIPT), "--root", str(ROOT), "--input", str(input_path), "--output", str(output), "--run-id", "TEST-RUN-004", "--format", "json"],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)

    # 5
    def test_missing_source_system_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self._load_json(SAMPLE_DIR / "minimal-valid-device.json")
            package["sourceSystemContext"] = {}
            input_path = Path(directory) / "missing-source.json"
            input_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
            output = Path(directory) / "out.json"
            result = subprocess.run(
                ["python3", str(RUNNER_SCRIPT), "--root", str(ROOT), "--input", str(input_path), "--output", str(output), "--run-id", "TEST-RUN-005", "--format", "json"],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)

    # 6-10
    def test_prohibited_password_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "out.json"
            result = self._run("prohibited-field-rejected.json", output, "TEST-RUN-006")
            self.assertNotEqual(result.returncode, 0)

    def test_bearer_token_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self._load_json(SAMPLE_DIR / "minimal-valid-device.json")
            package["devices"][0]["approvedMetadata"] = {"header": "Bearer sample-token"}
            input_path = Path(directory) / "bad-token.json"
            input_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
            output = Path(directory) / "out.json"
            result = subprocess.run(
                ["python3", str(RUNNER_SCRIPT), "--root", str(ROOT), "--input", str(input_path), "--output", str(output), "--run-id", "TEST-RUN-007", "--format", "json"],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)

    def test_private_key_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self._load_json(SAMPLE_DIR / "minimal-valid-device.json")
            package["devices"][0]["approvedMetadata"] = {"pem": "-----BEGIN PRIVATE KEY-----fake-----END PRIVATE KEY-----"}
            input_path = Path(directory) / "bad-key.json"
            input_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
            output = Path(directory) / "out.json"
            result = subprocess.run(
                ["python3", str(RUNNER_SCRIPT), "--root", str(ROOT), "--input", str(input_path), "--output", str(output), "--run-id", "TEST-RUN-008", "--format", "json"],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)

    def test_credential_connection_string_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self._load_json(SAMPLE_DIR / "minimal-valid-device.json")
            package["devices"][0]["approvedMetadata"] = {"dsn": "mysql://user:pass@example.test/db"}
            input_path = Path(directory) / "bad-dsn.json"
            input_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
            output = Path(directory) / "out.json"
            result = subprocess.run(
                ["python3", str(RUNNER_SCRIPT), "--root", str(ROOT), "--input", str(input_path), "--output", str(output), "--run-id", "TEST-RUN-009", "--format", "json"],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)

    def test_telemetry_value_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self._load_json(SAMPLE_DIR / "minimal-valid-device.json")
            package["devices"][0]["currentTelemetryValue"] = 42
            input_path = Path(directory) / "bad-telemetry.json"
            input_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
            output = Path(directory) / "out.json"
            result = subprocess.run(
                ["python3", str(RUNNER_SCRIPT), "--root", str(ROOT), "--input", str(input_path), "--output", str(output), "--run-id", "TEST-RUN-010", "--format", "json"],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)

    # 11-18
    def test_valid_device_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "valid-evidence.json"
            self.assertEqual(self._run("minimal-valid-device.json", output, "TEST-RUN-011").returncode, 0)
            payload = self._load_json(output)
            self.assertEqual(payload["status"], "OFFLINE_RECONCILIATION_EVIDENCE")

    def test_valid_device_point_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "valid-points-evidence.json"
            self.assertEqual(self._run("valid-device-with-points.json", output, "TEST-RUN-012").returncode, 0)
            payload = self._load_json(output)
            self.assertGreater(payload["pointClassificationResults"]["totalPoints"], 0)

    def test_identity_collision_blocker(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "identity-collision.json"
            self.assertEqual(self._run("identity-collision.json", output, "TEST-RUN-013").returncode, 0)
            payload = self._load_json(output)
            self.assertTrue(any("IDENTITY" in item for item in payload["blockers"]))

    def test_tenant_mismatch_blocker(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "scope-mismatch.json"
            self.assertEqual(self._run("scope-mismatch.json", output, "TEST-RUN-014").returncode, 0)
            payload = self._load_json(output)
            self.assertTrue(any("TENANT" in item for item in payload["blockers"]))

    def test_site_mismatch_blocker(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self._load_json(SAMPLE_DIR / "minimal-valid-device.json")
            package["devices"][0]["siteId"] = "site-other"
            input_path = Path(directory) / "site-mismatch.json"
            input_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
            output = Path(directory) / "out.json"
            result = subprocess.run(
                ["python3", str(RUNNER_SCRIPT), "--root", str(ROOT), "--input", str(input_path), "--output", str(output), "--run-id", "TEST-RUN-015", "--format", "json"],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0)
            payload = self._load_json(output)
            self.assertTrue(any("SITE" in item for item in payload["blockers"]))

    def test_missing_required_field_blocker(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "missing-required.json"
            self.assertEqual(self._run("missing-required-field.json", output, "TEST-RUN-016").returncode, 0)
            payload = self._load_json(output)
            self.assertIn("MISSING_STABLE_SOURCE_ID", payload["blockers"])

    def test_ambiguous_standard_field_review(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "ambiguous.json"
            self.assertEqual(self._run("ambiguous-standard-field.json", output, "TEST-RUN-017").returncode, 0)
            payload = self._load_json(output)
            self.assertIn("AMBIGUOUS_STANDARD_FIELD", payload["reviews"])

    def test_unresolved_parent_review(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "unresolved-parent.json"
            self.assertEqual(self._run("unresolved-parent.json", output, "TEST-RUN-018").returncode, 0)
            payload = self._load_json(output)
            self.assertTrue(any(item in payload["reviews"] for item in ("UNRESOLVED_PARENT", "UNRESOLVED_PARENT")))

    # 19-24
    def test_deterministic_input_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            out1 = Path(directory) / "a.json"
            out2 = Path(directory) / "b.json"
            self.assertEqual(self._run("valid-device-with-points.json", out1, "TEST-RUN-019").returncode, 0)
            self.assertEqual(self._run("valid-device-with-points.json", out2, "TEST-RUN-019").returncode, 0)
            self.assertEqual(self._load_json(out1)["inputDigest"], self._load_json(out2)["inputDigest"])

    def test_deterministic_result_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            out1 = Path(directory) / "a.json"
            out2 = Path(directory) / "b.json"
            self.assertEqual(self._run("valid-device-with-points.json", out1, "TEST-RUN-020").returncode, 0)
            self.assertEqual(self._run("valid-device-with-points.json", out2, "TEST-RUN-020").returncode, 0)
            self.assertEqual(self._load_json(out1)["resultDigest"], self._load_json(out2)["resultDigest"])

    def test_repeat_run_deterministic_output(self):
        with tempfile.TemporaryDirectory() as directory:
            out1 = Path(directory) / "a.json"
            out2 = Path(directory) / "b.json"
            self.assertEqual(self._run("valid-device-with-points.json", out1, "TEST-RUN-021").returncode, 0)
            self.assertEqual(self._run("valid-device-with-points.json", out2, "TEST-RUN-021").returncode, 0)
            self.assertEqual(out1.read_bytes(), out2.read_bytes())

    def test_input_ordering_does_not_change_semantics(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self._load_json(SAMPLE_DIR / "valid-device-with-points.json")
            package["standardFields"] = list(reversed(package["standardFields"]))
            custom = Path(directory) / "reversed.json"
            custom.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
            out1 = Path(directory) / "a.json"
            out2 = Path(directory) / "b.json"
            self.assertEqual(self._run("valid-device-with-points.json", out1, "TEST-RUN-022").returncode, 0)
            result = subprocess.run(
                ["python3", str(RUNNER_SCRIPT), "--root", str(ROOT), "--input", str(custom), "--output", str(out2), "--run-id", "TEST-RUN-022", "--format", "json"],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0)
            payload_a = self._load_json(out1)
            payload_b = self._load_json(out2)
            self.assertEqual(payload_a["resultDigest"], payload_b["resultDigest"])

    def test_changed_safe_field_changes_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self._load_json(SAMPLE_DIR / "minimal-valid-device.json")
            package["devices"][0]["description"] = "modified-safe-field"
            custom = Path(directory) / "modified.json"
            custom.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
            out1 = Path(directory) / "a.json"
            out2 = Path(directory) / "b.json"
            self.assertEqual(self._run("minimal-valid-device.json", out1, "TEST-RUN-023").returncode, 0)
            result = subprocess.run(
                ["python3", str(RUNNER_SCRIPT), "--root", str(ROOT), "--input", str(custom), "--output", str(out2), "--run-id", "TEST-RUN-023", "--format", "json"],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0)
            self.assertNotEqual(self._load_json(out1)["inputDigest"], self._load_json(out2)["inputDigest"])

    def test_prohibited_value_never_appears_in_errors_or_report(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self._load_json(SAMPLE_DIR / "minimal-valid-device.json")
            package["devices"][0]["approvedMetadata"] = {"secretHint": "password=super-secret"}
            custom = Path(directory) / "prohibited-value.json"
            custom.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
            output = Path(directory) / "out.json"
            result = subprocess.run(
                ["python3", str(RUNNER_SCRIPT), "--root", str(ROOT), "--input", str(custom), "--output", str(output), "--run-id", "TEST-RUN-024", "--format", "json"],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("super-secret", result.stdout + result.stderr)

    def test_prohibited_value_never_appears_in_report_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self._load_json(SAMPLE_DIR / "minimal-valid-device.json")
            package["devices"][0]["approvedMetadata"] = {"secretHint": "token=hidden-value"}
            custom = Path(directory) / "bad-value.json"
            custom.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
            output = Path(directory) / "out.json"
            result = subprocess.run(
                ["python3", str(RUNNER_SCRIPT), "--root", str(ROOT), "--input", str(custom), "--output", str(output), "--run-id", "TEST-RUN-025", "--format", "json"],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            if output.exists():
                self.assertNotIn("hidden-value", output.read_text(encoding="utf-8"))

    # 26-31
    def test_no_database_import_or_connection_or_writes(self):
        text = MODULE_FILE.read_text(encoding="utf-8").lower()
        self.assertNotIn("sqlalchemy", text)
        self.assertNotIn("create_engine", text)
        self.assertNotIn("db.session", text)
        self.assertNotIn("insert into", text)
        self.assertNotIn("update ", text)
        self.assertNotIn("delete from", text)
        self.assertNotIn("add_device(", text)
        self.assertNotIn("add_point(", text)

    def test_no_legacy_write_pattern(self):
        text = MODULE_FILE.read_text(encoding="utf-8")
        self.assertNotIn("IMSDevice(", text)
        self.assertNotIn("dao.", text.lower())
        self.assertNotIn("session.commit", text.lower())

    def test_no_canonical_write_pattern(self):
        text = MODULE_FILE.read_text(encoding="utf-8")
        self.assertNotIn(".add_device(", text)
        self.assertNotIn(".add_point(", text)
        self.assertNotIn(".add_tag(", text)
        self.assertNotIn(".add_relationship(", text)

    def test_fail_on_blocker_behavior(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "out.json"
            result = self._run("identity-collision.json", output, "TEST-RUN-030", ["--fail-on-blocker"])
            self.assertNotEqual(result.returncode, 0)

    def test_fail_on_review_behavior(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "out.json"
            result = self._run("ambiguous-standard-field.json", output, "TEST-RUN-031", ["--fail-on-review"])
            self.assertNotEqual(result.returncode, 0)

    # 32-35
    def test_check_matching_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory) / "base.json"
            out = Path(directory) / "out.json"
            self.assertEqual(self._run("valid-device-with-points.json", base, "TEST-RUN-032").returncode, 0)
            result = self._run("valid-device-with-points.json", out, "TEST-RUN-032", ["--check", str(base)])
            self.assertEqual(result.returncode, 0)

    def test_check_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory) / "base.json"
            out = Path(directory) / "out.json"
            self.assertEqual(self._run("minimal-valid-device.json", base, "TEST-RUN-033-A").returncode, 0)
            result = self._run("valid-device-with-points.json", out, "TEST-RUN-033-B", ["--check", str(base)])
            self.assertNotEqual(result.returncode, 0)

    def test_run_id_only_comparison_behavior(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory) / "base.json"
            out = Path(directory) / "out.json"
            self.assertEqual(self._run("valid-device-with-points.json", base, "TEST-RUN-034-A").returncode, 0)
            result = self._run(
                "valid-device-with-points.json",
                out,
                "TEST-RUN-034-B",
                ["--check", str(base), "--allow-run-id-only-diff"],
            )
            self.assertEqual(result.returncode, 0)

    def test_output_contains_no_absolute_path_or_timestamp(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "out.json"
            self.assertEqual(self._run("valid-device-with-points.json", output, "TEST-RUN-035").returncode, 0)
            payload = self._load_json(output)
            self.assertFalse(str(Path.home()) in json.dumps(payload))
            self.assertNotIn("generatedAt", payload)

    def test_check_mismatch_without_allow_run_id_only_diff(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory) / "base.json"
            out = Path(directory) / "out.json"
            self.assertEqual(self._run("valid-device-with-points.json", base, "TEST-RUN-036-A").returncode, 0)
            result = self._run(
                "valid-device-with-points.json",
                out,
                "TEST-RUN-036-B",
                ["--check", str(base)],
            )
            self.assertNotEqual(result.returncode, 0)

    # 37-40
    def test_output_cannot_declare_ready_for_write_cutover(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "out.json"
            self.assertEqual(self._run("minimal-valid-device.json", output, "TEST-RUN-037").returncode, 0)
            self.assertNotEqual(self._load_json(output)["cutoverDecision"], "READY_FOR_WRITE_CUTOVER")

    def test_samples_are_synthetic(self):
        for sample_name in (
            "minimal-valid-device.json",
            "valid-device-with-points.json",
            "identity-collision.json",
            "scope-mismatch.json",
            "missing-required-field.json",
            "ambiguous-standard-field.json",
            "unresolved-parent.json",
        ):
            content = (SAMPLE_DIR / sample_name).read_text(encoding="utf-8").lower()
            self.assertIn("synthetic", content)
            self.assertNotIn("prod-", content)
            self.assertNotIn("customer-real", content)

    def test_no_public_api_added(self):
        text = MODULE_FILE.read_text(encoding="utf-8")
        self.assertNotIn("@api_bp.route", text)
        self.assertNotIn("Blueprint", text)

    def test_existing_facade_and_reconciliation_are_reused(self):
        text = MODULE_FILE.read_text(encoding="utf-8")
        self.assertIn("LegacyDeviceReadCompatibilityFacade", text)
        self.assertIn("DeviceProjectionReconciliationService", text)

    def test_validation_statement_declares_read_only_offline_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "out.json"
            self.assertEqual(self._run("minimal-valid-device.json", output, "TEST-RUN-040").returncode, 0)
            payload = self._load_json(output)
            statement = payload.get("validationStatement", "").lower()
            self.assertIn("read-only", statement)
            self.assertIn("no database access", statement)


if __name__ == "__main__":
    unittest.main()
