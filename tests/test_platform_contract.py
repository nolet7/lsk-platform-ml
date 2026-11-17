import json
import pytest
from mlplatform.manifest import validate_image, target_namespace, workload
from mlplatform.schemas import ModelRegistration

IMAGE="123456789012.dkr.ecr.us-east-1.amazonaws.com/tenant-model@sha256:"+"a"*64

@pytest.fixture(autouse=True)
def config(monkeypatch):
    monkeypatch.setenv("AWS_ACCOUNT_ID","123456789012")
    monkeypatch.setenv("AWS_REGION","us-east-1")
    monkeypatch.setenv("TENANT_NAMESPACE_MAP",json.dumps({"tenant-a":{"stage":"tenant-a-stage","production":"tenant-a-prod"}}))

def test_immutable_ecr_and_region_scope():
    validate_image(IMAGE)
    with pytest.raises(ValueError):
        validate_image(IMAGE.replace("@sha256:",":latest-"))
    with pytest.raises(ValueError):
        validate_image(IMAGE.replace("123456789012","111111111111"))

def test_tenant_namespace_fail_closed():
    assert target_namespace("tenant-a","production")=="tenant-a-prod"
    with pytest.raises(ValueError):
        target_namespace("tenant-b","production")
    with pytest.raises(ValueError):
        target_namespace("../tenant-a","production")

def test_serving_manifest_is_isolated_and_non_root():
    ns, dep, svc=workload("tenant-a","blade-quality",IMAGE,3,"production",4)
    assert ns=="tenant-a-prod"
    spec=dep["spec"]["template"]["spec"]
    assert spec["automountServiceAccountToken"] is False
    assert spec["containers"][0]["image"]==IMAGE
    assert spec["containers"][0]["securityContext"]["readOnlyRootFilesystem"] is True
    assert dep["spec"]["template"]["metadata"]["annotations"]["lsk.ai/deployment-revision"]=="4"
    assert svc["spec"]["type"]=="ClusterIP"

def test_registry_contract_needs_evaluation_lineage():
    with pytest.raises(Exception):
        ModelRegistration(name="blade-quality",version="1",image=IMAGE,
                          evaluation_reference="",source_run_id="r1",model_artifact_uri="models:/m/1")
