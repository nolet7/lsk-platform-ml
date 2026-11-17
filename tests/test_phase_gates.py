import json
from scripts.verify_phase_gates import APPROVERS, CONTROLS, main, verify

def sample(phase):
    return {"phases": {phase: {"controls": {
        k: {"status": "complete", "evidence": ["https://tickets.internal.test/change/123"]}
        for k in CONTROLS[phase]},
        "approvals": [
            {"role": role, "signer": "Synthetic Reviewer", "timestamp": "2026-11-16T00:00:00Z",
             "reference": "https://tickets.internal.test/approvals/123"}
            for role in APPROVERS[phase]]
    }}}

def test_complete_structure_is_only_structural():
    for phase in CONTROLS:
        assert verify(sample(phase), phase) == []

def test_no_auto_approval_from_documentation():
    m = sample("production")
    m["phases"]["production"]["controls"]["PROD-DR"]["status"] = "pending"
    assert any("not complete" in e for e in verify(m, "production"))

def test_missing_signer_is_blocked():
    m = sample("poc")
    m["phases"]["poc"]["approvals"][0]["signer"] = ""
    assert any("signed approval" in e for e in verify(m, "poc"))

def test_example_manifest_rejected(tmp_path):
    path = tmp_path / "sample.json"
    path.write_text(json.dumps({"phases":{"poc":{"controls":{},"approvals":[]}}}))
    assert main([str(path), "--phase", "poc"]) == 1

def test_invalid_manifest_rejected(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{")
    assert main([str(path)]) == 2
