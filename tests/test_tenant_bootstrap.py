import json
import pytest
from production.scripts.render_tenant_bootstrap import build

def test_bootstrap_rbac_scopes_only_tenant_namespace(monkeypatch):
    mapping={"tenant-a":{"stage":"tenant-a-stage","production":"tenant-a-prod"}}
    output=build(mapping)
    assert len(output["items"])==18
    roles=[x for x in output["items"] if x["kind"]=="Role"]
    assert len(roles)==4
    assert all(x["metadata"]["namespace"].startswith("tenant-a-") for x in roles)
    assert all("delete" not in set(v for rule in x["rules"] for v in rule["verbs"]) for x in roles)

def test_different_tenants_cannot_share_namespace():
    with pytest.raises(ValueError):
        build({"tenant-a":{"stage":"dup","production":"pa"},
               "tenant-b":{"stage":"dup","production":"pb"}})
