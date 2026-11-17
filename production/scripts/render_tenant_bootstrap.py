"""Render limited RBAC for each approved tenant namespace. Cluster admin applies.

Use: python production/scripts/render_tenant_bootstrap.py --mapping config.json > /tmp/bootstrap.json
Mapping format: {"tenant-a":{"stage":"tenant-a-stage","production":"tenant-a-prod"}}
"""
import argparse
import json
from pathlib import Path
from mlplatform.manifest import target_namespace

def build(mapping):
    import os
    os.environ["TENANT_NAMESPACE_MAP"] = json.dumps(mapping)
    items=[]
    used=set()
    for tenant,envs in mapping.items():
        for environment in ("stage","production"):
            namespace=target_namespace(tenant,environment)
            if namespace in used:
                raise ValueError("each tenant/environment requires its own namespace")
            used.add(namespace)
            items.extend([
                {"apiVersion":"v1","kind":"Namespace",
                 "metadata":{"name":namespace,"labels":{
                     "lsk.ai/tenant":tenant,"lsk.ai/environment":environment,
                     "pod-security.kubernetes.io/enforce":"restricted"}}},
                {"apiVersion":"v1","kind":"ServiceAccount",
                 "metadata":{"name":"ml-model-serving","namespace":namespace}},
                {"apiVersion":"rbac.authorization.k8s.io/v1","kind":"Role",
                 "metadata":{"name":"ml-platform-workload-controller","namespace":namespace},
                 "rules":[
                     {"apiGroups":["apps"],"resources":["deployments"],"verbs":["get","create","patch"]},
                     {"apiGroups":[""],"resources":["services"],"verbs":["get","create"]}
                 ]},
                {"apiVersion":"rbac.authorization.k8s.io/v1","kind":"RoleBinding",
                 "metadata":{"name":"ml-platform-controller","namespace":namespace},
                 "subjects":[{"kind":"ServiceAccount","name":"ml-platform-controller","namespace":"ml-quality"}],
                 "roleRef":{"kind":"Role","name":"ml-platform-workload-controller",
                            "apiGroup":"rbac.authorization.k8s.io"}}
                {"apiVersion":"rbac.authorization.k8s.io/v1","kind":"Role",
                 "metadata":{"name":"ml-platform-read-only","namespace":namespace},
                 "rules":[{"apiGroups":["apps"],"resources":["deployments"],"verbs":["get"]}]},
                {"apiVersion":"rbac.authorization.k8s.io/v1","kind":"RoleBinding",
                 "metadata":{"name":"ml-platform-reader","namespace":namespace},
                 "subjects":[{"kind":"ServiceAccount","name":"ml-platform-reader","namespace":"ml-quality"}],
                 "roleRef":{"kind":"Role","name":"ml-platform-read-only",
                            "apiGroup":"rbac.authorization.k8s.io"}},
                {"apiVersion":"v1","kind":"ResourceQuota",
                 "metadata":{"name":"ml-serving-quota","namespace":namespace},
                 "spec":{"hard":{"requests.cpu":"12","requests.memory":"32Gi",
                                  "limits.cpu":"24","limits.memory":"64Gi",
                                  "pods":"36","services":"12"}}},
                {"apiVersion":"v1","kind":"LimitRange",
                 "metadata":{"name":"ml-serving-limits","namespace":namespace},
                 "spec":{"limits":[{"type":"Container","defaultRequest":{"cpu":"250m","memory":"512Mi"},
                                     "default":{"cpu":"2","memory":"2Gi"},
                                     "max":{"cpu":"4","memory":"8Gi"}}]}},
                {"apiVersion":"networking.k8s.io/v1","kind":"NetworkPolicy",
                 "metadata":{"name":"tenant-default-deny","namespace":namespace},
                 "spec":{"podSelector":{},"policyTypes":["Ingress","Egress"]}}
            ])
    return {"apiVersion":"v1","kind":"List","items":items}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mapping",required=True,type=Path)
    args=p.parse_args()
    mapping=json.loads(args.mapping.read_text())
    print(json.dumps(build(mapping),indent=2))

if __name__=="__main__":
    main()
