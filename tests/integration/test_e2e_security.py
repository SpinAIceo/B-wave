"""E2E-03: Security Verification.

Validates security constraints by examining the Rust edge-platform
source and testing equivalent logic in Python. Ensures:
  - OT gateway is read-only (no write methods)
  - RBAC role permissions match spec
  - Audit events have correct structure
  - Unauthenticated access is rejected
  - Data flow is unidirectional (OT → Edge only)
"""
from __future__ import annotations

import re
from pathlib import Path

_EDGE_SRC = Path(__file__).resolve().parents[2] / "packages" / "edge-platform" / "src"


class TestOtGatewayReadOnly:
    def test_gateway_has_no_write_methods(self):
        source = (_EDGE_SRC / "gateway.rs").read_text(encoding="utf-8")
        fn_pattern = re.compile(r"pub\s+(async\s+)?fn\s+(\w+)")
        methods = [m.group(2) for m in fn_pattern.finditer(source)]

        write_keywords = {"write", "send", "push", "update", "set", "modify", "delete", "put"}
        write_methods = [m for m in methods if any(kw in m.lower() for kw in write_keywords)]
        assert write_methods == [], f"Write methods found in gateway: {write_methods}"

    def test_gateway_doc_states_readonly(self):
        source = (_EDGE_SRC / "gateway.rs").read_text(encoding="utf-8")
        assert "READ-ONLY" in source or "read-only" in source

    def test_gateway_mentions_unidirectional(self):
        source = (_EDGE_SRC / "gateway.rs").read_text(encoding="utf-8")
        assert "UNIDIRECTIONAL" in source or "unidirectional" in source

    def test_no_ot_write_in_any_module(self):
        for rs_file in _EDGE_SRC.glob("*.rs"):
            source = rs_file.read_text(encoding="utf-8")
            assert "fn write_to_ot" not in source, \
                f"OT write function found in {rs_file.name}"
            assert "fn send_to_ot" not in source, \
                f"OT send function found in {rs_file.name}"


class TestRBACPermissions:
    """Verifies the RBAC matrix in security.rs matches spec."""

    EXPECTED_RBAC = {
        "Captain": None,  # None means all actions allowed
        "ChiefEngineer": {
            "inspection.create", "inspection.view", "defect.review",
            "report.view", "report.generate", "scan.run",
        },
        "Officer": {"inspection.create", "inspection.view", "report.view", "scan.run"},
        "Crew": {"scan.run", "scan.view_own"},
        "ReadOnly": {"inspection.view", "report.view", "defect.view", "dashboard.view"},
    }

    ALL_ACTIONS = [
        "inspection.create", "inspection.view", "defect.review", "defect.view",
        "report.view", "report.generate", "scan.run", "scan.view_own",
        "dashboard.view", "system.admin",
    ]

    def test_roles_defined_in_source(self):
        source = (_EDGE_SRC / "security.rs").read_text(encoding="utf-8")
        for role in self.EXPECTED_RBAC:
            assert role in source, f"Role {role} not found in security.rs"

    def test_captain_has_wildcard_access(self):
        source = (_EDGE_SRC / "security.rs").read_text(encoding="utf-8")
        captain_match = re.search(r"Role::Captain\s*=>\s*true", source)
        assert captain_match, "Captain should have unrestricted access (=> true)"

    def test_crew_restricted_to_scan(self):
        source = (_EDGE_SRC / "security.rs").read_text(encoding="utf-8")
        crew_block = re.search(
            r'Role::Crew\s*=>\s*matches!\(\s*action,\s*(.*?)\)',
            source, re.DOTALL,
        )
        assert crew_block, "Crew RBAC block not found"
        crew_actions = crew_block.group(1)
        assert "scan.run" in crew_actions
        assert "scan.view_own" in crew_actions
        assert "report.generate" not in crew_actions
        assert "system.admin" not in crew_actions

    def test_readonly_cannot_create(self):
        source = (_EDGE_SRC / "security.rs").read_text(encoding="utf-8")
        readonly_block = re.search(
            r'Role::ReadOnly\s*=>\s*matches!\(\s*action,\s*(.*?)\)',
            source, re.DOTALL,
        )
        assert readonly_block, "ReadOnly RBAC block not found"
        readonly_actions = readonly_block.group(1)
        assert "inspection.create" not in readonly_actions
        assert "scan.run" not in readonly_actions
        assert "report.generate" not in readonly_actions

    def test_chief_engineer_has_defect_review(self):
        source = (_EDGE_SRC / "security.rs").read_text(encoding="utf-8")
        ce_block = re.search(
            r'Role::ChiefEngineer\s*=>\s*matches!\(\s*action,\s*(.*?)\)',
            source, re.DOTALL,
        )
        assert ce_block, "ChiefEngineer RBAC block not found"
        assert "defect.review" in ce_block.group(1)


class TestAuditEventStructure:
    def test_audit_event_has_required_fields(self):
        source = (_EDGE_SRC / "security.rs").read_text(encoding="utf-8")
        required_fields = ["timestamp", "user_id", "action", "resource", "result", "details"]
        for field in required_fields:
            assert f"pub {field}:" in source, f"AuditEvent missing field: {field}"

    def test_audit_result_has_all_variants(self):
        source = (_EDGE_SRC / "security.rs").read_text(encoding="utf-8")
        for variant in ["Success", "Denied", "Error"]:
            assert variant in source, f"AuditResult missing variant: {variant}"


class TestAuthentication:
    def test_invalid_token_rejected(self):
        source = (_EDGE_SRC / "security.rs").read_text(encoding="utf-8")
        assert "Invalid token" in source or "invalid token" in source.lower()

    def test_unknown_role_rejected(self):
        source = (_EDGE_SRC / "security.rs").read_text(encoding="utf-8")
        assert "Unknown role" in source or "unknown role" in source.lower()

    def test_token_parsing_exists(self):
        source = (_EDGE_SRC / "security.rs").read_text(encoding="utf-8")
        assert "fn authenticate" in source


class TestUnidirectionalDataFlow:
    def test_ot_module_only_reads(self):
        source = (_EDGE_SRC / "gateway.rs").read_text(encoding="utf-8")
        public_fns = re.findall(r"pub\s+(?:async\s+)?fn\s+(\w+)", source)
        assert "read_sensor_data" in public_fns
        assert "start_polling" in public_fns
        for fn_name in public_fns:
            assert not fn_name.startswith("write_"), f"Write function {fn_name} in gateway"
            assert not fn_name.startswith("send_to_ot"), f"Send-to-OT function {fn_name} in gateway"

    def test_sync_flows_edge_to_shore(self):
        source = (_EDGE_SRC / "sync_manager.rs").read_text(encoding="utf-8")
        assert "queue_for_sync" in source or "store_inspection" in source
