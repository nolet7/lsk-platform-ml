from types import SimpleNamespace
from mlplatform import controller
import pytest

def test_observed_health_requires_actual_available_replicas(monkeypatch):
    monkeypatch.setenv("TENANT_NAMESPACE_MAP",'{"tenant-a":{"stage":"a-stage","production":"a-prod"}}')
    class DummyApi:
        def read_namespaced_deployment(self,name,namespace):
            assert name=="ml-example" and namespace=="a-prod"
            return SimpleNamespace(
                metadata=SimpleNamespace(labels={"lsk.ai/tenant":"tenant-a","lsk.ai/managed-by":"ml-platform"},
                                         generation=2),
                spec=SimpleNamespace(replicas=3,template=SimpleNamespace(
                    spec=SimpleNamespace(containers=[SimpleNamespace(image='image-a')]),
                    metadata=SimpleNamespace(annotations={'lsk.ai/deployment-revision':'4'}))),
                status=SimpleNamespace(available_replicas=2,observed_generation=2))
    from kubernetes import config,client
    monkeypatch.setattr(config,"load_incluster_config",lambda:None)
    monkeypatch.setattr(client,"AppsV1Api",lambda:DummyApi())
    status=controller.observe("tenant-a","example","production",
                              expected_image="image-a",expected_revision=4)
    assert status["healthy"] is False
    assert status["available_replicas"]==2
    assert status["desired_replicas"]==3
    assert status["matches_expected_image"] is True
    assert controller.observe("tenant-a","example","production",expected_image="image-b")["healthy"] is False
