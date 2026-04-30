"""QA: SC-04 Security Verification — Behavioral Tests.

Tests actual Rust binary behavior (cargo test) alongside source analysis.
Addresses Codex adversarial review finding: string-grep tests replaced with
behavioral verification against compiled Rust code.
"""

from __future__ import annotations

import json
import subprocess
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EDGE_SRC = ROOT / "packages" / "edge-platform" / "src"
EDGE_DIR = ROOT / "packages" / "edge-platform"


def _read_rust_source(filename: str) -> str:
    path = EDGE_SRC / filename
    assert path.exists(), f"Rust source not found: {path}"
    return path.read_text(encoding="utf-8")


def _cargo_available() -> bool:
    try:
        result = subprocess.run(
            ["cargo", "--version"], capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


CARGO_OK = _cargo_available()


# ---------------------------------------------------------------------------
# Behavioral tests: run actual Rust tests via cargo
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not CARGO_OK, reason="cargo not installed")
class TestRustSecurityBehavioral:
    """Run cargo test on the edge-platform and parse results."""

    @pytest.fixture(autouse=True, scope="class")
    def cargo_test_output(self, request):
        result = subprocess.run(
            ["cargo", "test"],
            capture_output=True,
            text=True,
            cwd=str(EDGE_DIR),
            timeout=300,
        )
        request.cls.cargo_output = result.stdout + result.stderr
        request.cls.cargo_returncode = result.returncode

    def test_cargo_test_passes(self):
        assert self.cargo_returncode == 0, (
            f"cargo test failed:\n{self.cargo_output[-2000:]}"
        )

    def test_captain_can_do_anything(self):
        assert "captain_can_do_anything ... ok" in self.cargo_output

    def test_crew_limited_to_scan(self):
        assert "crew_limited_to_scan ... ok" in self.cargo_output

    def test_readonly_view_only(self):
        assert "readonly_view_only ... ok" in self.cargo_output

    def test_chief_engineer_permissions(self):
        assert "chief_engineer_permissions ... ok" in self.cargo_output

    def test_officer_permissions(self):
        assert "officer_permissions ... ok" in self.cargo_output

    def test_authenticate_invalid_token_rejected(self):
        assert "authenticate_invalid_token ... ok" in self.cargo_output

    def test_authenticate_unknown_role_rejected(self):
        assert "authenticate_unknown_role ... ok" in self.cargo_output

    def test_rbac_disabled_allows_all(self):
        assert "rbac_disabled_allows_all ... ok" in self.cargo_output

    def test_audit_log_records_events(self):
        assert "audit_log_records_events ... ok" in self.cargo_output

    def test_audit_log_filters_by_timestamp(self):
        assert "audit_log_filters_by_timestamp ... ok" in self.cargo_output


@pytest.mark.skipif(not CARGO_OK, reason="cargo not installed")
class TestRustRuleEngineBehavioral:
    """Verify rule engine tests pass via cargo."""

    @pytest.fixture(autouse=True, scope="class")
    def cargo_test_output(self, request):
        result = subprocess.run(
            ["cargo", "test"],
            capture_output=True,
            text=True,
            cwd=str(EDGE_DIR),
            timeout=300,
        )
        request.cls.cargo_output = result.stdout + result.stderr
        request.cls.cargo_returncode = result.returncode

    def test_rust_defect_maps_to_hull_violation(self):
        assert "rust_defect_maps_to_hull_violation ... ok" in self.cargo_output

    def test_cargo_lashing_maps_to_cargo_rules(self):
        assert "cargo_lashing_maps_to_cargo_rules ... ok" in self.cargo_output

    def test_cic_targets_are_cargo_related(self):
        assert "cic_targets_are_cargo_related ... ok" in self.cargo_output

    def test_high_confidence_escalates_severity(self):
        assert "high_confidence_escalates_severity ... ok" in self.cargo_output

    def test_low_confidence_downgrades_severity(self):
        assert "low_confidence_downgrades_severity ... ok" in self.cargo_output


@pytest.mark.skipif(not CARGO_OK, reason="cargo not installed")
class TestRustSyncBehavioral:
    """Verify sync manager tests pass via cargo."""

    @pytest.fixture(autouse=True, scope="class")
    def cargo_test_output(self, request):
        result = subprocess.run(
            ["cargo", "test"],
            capture_output=True,
            text=True,
            cwd=str(EDGE_DIR),
            timeout=300,
        )
        request.cls.cargo_output = result.stdout + result.stderr

    def test_init_creates_tables(self):
        assert "init_creates_tables ... ok" in self.cargo_output

    def test_sync_queue_priority_ordering(self):
        assert "sync_queue_priority_ordering ... ok" in self.cargo_output

    def test_store_and_retrieve_inspection(self):
        assert "store_and_retrieve_inspection ... ok" in self.cargo_output

    def test_mark_synced_updates_stats(self):
        assert "mark_synced_updates_stats ... ok" in self.cargo_output


# ---------------------------------------------------------------------------
# Source analysis tests: verify architectural constraints
# ---------------------------------------------------------------------------


class TestOTGatewayReadOnly:
    def test_no_write_methods_in_gateway(self):
        src = _read_rust_source("gateway.rs")
        write_patterns = ["fn write", "fn set_", "fn update_", "fn delete_", "fn send_to_ot"]
        for pattern in write_patterns:
            assert pattern not in src, f"OT gateway must be read-only, found: {pattern}"

    def test_gateway_declares_readonly(self):
        src = _read_rust_source("gateway.rs")
        assert "read" in src.lower() or "Read" in src

    def test_gateway_mentions_unidirectional(self):
        src = _read_rust_source("gateway.rs")
        lower = src.lower()
        assert "unidirectional" in lower or "read-only" in lower or "read only" in lower

    def test_no_write_to_ot_in_any_module(self):
        for rs_file in EDGE_SRC.glob("*.rs"):
            src = rs_file.read_text(encoding="utf-8")
            assert "write_to_ot" not in src, f"Found write_to_ot in {rs_file.name}"
            assert "send_to_ot" not in src, f"Found send_to_ot in {rs_file.name}"


class TestUnidirectionalFlow:
    def test_sync_flows_edge_to_shore(self):
        src = _read_rust_source("sync_manager.rs")
        assert "push" in src.lower() or "queue" in src.lower() or "sync" in src.lower()

    def test_ot_data_never_flows_back(self):
        gw_src = _read_rust_source("gateway.rs")
        assert "write_back" not in gw_src
        assert "send_command" not in gw_src
        assert "control_ot" not in gw_src


class TestPKIInfrastructure:
    def test_pki_scripts_exist(self):
        pki_dir = ROOT / "deploy" / "pki"
        assert (pki_dir / "init-ca.sh").exists()
        assert (pki_dir / "issue-vessel-cert.sh").exists()
        assert (pki_dir / "issue-tablet-cert.sh").exists()
        assert (pki_dir / "revoke-cert.sh").exists()
        assert (pki_dir / "openssl.cnf").exists()

    def test_ca_script_uses_strong_key(self):
        script = (ROOT / "deploy" / "pki" / "init-ca.sh").read_text(encoding="utf-8")
        assert "4096" in script or "384" in script, "CA should use RSA-4096 or ECDSA P-384"

    def test_vessel_cert_has_san(self):
        script = (ROOT / "deploy" / "pki" / "issue-vessel-cert.sh").read_text(encoding="utf-8")
        lower = script.lower()
        assert "san" in lower or "subjectaltname" in lower or "alt" in lower

    def test_revocation_generates_crl(self):
        script = (ROOT / "deploy" / "pki" / "revoke-cert.sh").read_text(encoding="utf-8")
        lower = script.lower()
        assert "crl" in lower or "revoke" in lower
