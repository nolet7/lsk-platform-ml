from mlplatform import reconciler
from uuid import uuid4

def job():
    return {
        "id":str(uuid4()),"tenant_id":"a","name":"foo","environment":"production",
        "revision":4,"image":"immutable-image","replicas":2,"claim_token":str(uuid4())
    }

class Fake:
    def __init__(self,newer=False):
        self.j=job()
        self.events=[]
        self.newer=newer
    def claim(self):
        return self.j
    def has_newer_revision(self,*args):
        return self.newer
    def complete(self,*args):
        self.events.append(("done",args[-1]))
    def retry(self,*args):
        self.events.append(("retry",args[-1]))

def test_worker_records_success(monkeypatch):
    s=Fake()
    monkeypatch.setattr(reconciler.controller,"apply",lambda *args:None)
    assert reconciler.run_once(s) is True
    assert s.events == [("done","submitted")]

def test_worker_skips_obsolete_revision(monkeypatch):
    s=Fake(newer=True)
    def unexpected(*args):
        raise AssertionError("stale deployment was applied")
    monkeypatch.setattr(reconciler.controller,"apply",unexpected)
    assert reconciler.run_once(s)
    assert s.events == [("done","superseded")]

def test_worker_retries_failed_k8s_operation(monkeypatch):
    s=Fake()
    def fail(*args):
        raise RuntimeError("cluster unavailable")
    monkeypatch.setattr(reconciler.controller,"apply",fail)
    assert reconciler.run_once(s)
    assert s.events[0][0] == "retry"

def test_worker_idle():
    class Empty:
        def claim(self):
            return None
    assert reconciler.run_once(Empty()) is False
