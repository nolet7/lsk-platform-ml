"""Release and RBAC regression tests; these are static, not a live EKS validation."""
from pathlib import Path
import yaml
from production.scripts.render_tenant_bootstrap import build

def test_api_reader_and_worker_separation():
    manifest=list(yaml.safe_load_all(Path("production/k8s/ml-platform-api.yaml").read_text()))
    api=manifest[0]
    worker=yaml.safe_load(Path("production/k8s/mlplatform-worker.yaml").read_text())
    assert api["spec"]["template"]["spec"]["serviceAccountName"]=="ml-platform-reader"
    assert worker["spec"]["template"]["spec"]["serviceAccountName"]=="ml-platform-controller"

def test_tenant_role_bindings():
    m=build({"tenant-a":{"stage":"a-stage","production":"a-prod"}})
    roles=[i for i in m["items"] if i["kind"]=="Role"]
    api=[i for i in roles if i["metadata"]["name"]=="ml-platform-read-only"]
    assert len(api)==2
    assert all(r["rules"][0]["verbs"]==["get"] for r in api)
    assert len([i for i in m["items"] if i["kind"]=="NetworkPolicy"])==2

def test_worker_release_image_placeholder():
    template=Path("production/k8s/mlplatform-worker.yaml").read_text()
    assert template.count("REPLACE_WITH_APPROVED_ECR_IMAGE_DIGEST")==1
