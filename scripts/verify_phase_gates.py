"""Check structural completeness of external phase-gate evidence; never authenticates it."""
import argparse
import json
import sys
from pathlib import Path

CONTROLS = {
    "poc": ("POC-API", "POC-TESTS", "POC-LINEAGE", "POC-SAFETY"),
    "pilot": ("PILOT-IDENTITY", "PILOT-MLFLOW", "PILOT-JOBS", "PILOT-OBS", "PILOT-ADOPTION"),
    "production": ("PROD-INFRA", "PROD-SECURITY", "PROD-RELEASE", "PROD-DR", "PROD-SLO", "PROD-CAB"),
    "handover": ("OPS-RUNBOOK", "OPS-RECOVERY", "OPS-OWNERSHIP"),
}
APPROVERS = {
    "poc": ("product_owner", "quality", "platform"),
    "pilot": ("product_owner", "quality", "security", "ml_lead", "sre_lead"),
    "production": ("cto_delegate", "quality", "security", "platform_sre", "change_manager"),
    "handover": ("service_owner", "platform_sre", "quality", "product_owner"),
}

def verify(manifest, phase):
    issues = []
    phases = manifest.get("phases")
    if not isinstance(phases, dict):
        return ["phases must be an object"]
    target = phases.get(phase)
    if not isinstance(target, dict):
        return [f"{phase}: missing phase object"]
    controls = target.get("controls")
    if not isinstance(controls, dict):
        return [f"{phase}: missing controls object"]
    for name in CONTROLS[phase]:
        item = controls.get(name)
        if not isinstance(item, dict):
            issues.append(f"{phase}/{name}: missing control")
            continue
        if item.get("status") != "complete":
            issues.append(f"{phase}/{name}: not complete")
        evidence = item.get("evidence")
        if not isinstance(evidence, list) or not evidence or not all(
            isinstance(ref, str) and ref.strip() and not any(
                token in ref.lower() for token in ("example", "placeholder", "todo", "tbd")
            ) for ref in evidence
        ):
            issues.append(f"{phase}/{name}: missing real evidence reference")
    approvals = target.get("approvals")
    if not isinstance(approvals, list):
        return issues + [f"{phase}: approvals must be a list"]
    for role in APPROVERS[phase]:
        found = any(isinstance(a, dict) and a.get("role") == role
                    and all(isinstance(a.get(k), str) and a[k].strip()
                            for k in ("signer", "timestamp", "reference"))
                    and not any(token in a["reference"].lower()
                                for token in ("example", "placeholder", "todo", "tbd"))
                    for a in approvals)
        if not found:
            issues.append(f"{phase}: missing {role} signed approval reference")
    return issues

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("manifest", type=Path)
    p.add_argument("--phase", choices=tuple(CONTROLS), default=None)
    args = p.parse_args(argv)
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict):
            raise ValueError("manifest root must be an object")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"INVALID MANIFEST: {exc}", file=sys.stderr)
        return 2
    problems = []
    for phase in (args.phase,) if args.phase else CONTROLS:
        problems.extend(verify(manifest, phase))
    if problems:
        print(f"NOT READY ({len(problems)} issue(s))")
        for issue in problems:
            print(f"- {issue}")
        return 1
    print("STRUCTURALLY READY — human verification of actual artifacts and signer authority still required")
    return 0

if __name__ == "__main__":
    sys.exit(main())
