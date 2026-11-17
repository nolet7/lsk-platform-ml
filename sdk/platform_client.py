"""ML platform SDK: no Kubernetes manifests required from ML engineering clients."""
import httpx

class MLPlatformClient:
    def __init__(self, base_url: str, access_token: str, timeout: float = 15):
        if not base_url or not access_token:
            raise ValueError("platform URL and OIDC token are required")
        self.client = httpx.Client(base_url=base_url, timeout=timeout,
                                   headers={"Authorization":f"Bearer {access_token}"})

    def _request(self, method, path, **kwargs):
        response=self.client.request(method,path,**kwargs)
        response.raise_for_status()
        return response.json()

    def register_model(self, *, name, version, image, source_run_id, model_artifact_uri,
                       evaluation_reference):
        return self._request("POST","/v1/platform/models",json={
            "name":name,"version":version,"image":image,
            "source_run_id":source_run_id,"model_artifact_uri":model_artifact_uri,
            "evaluation_reference":evaluation_reference
        })

    def approve_model(self, model_id, reason):
        return self._request("POST",f"/v1/platform/models/{model_id}/approve",
                             json={"reason":reason})

    def deploy_model(self, *, model_id, name, environment, replicas=2):
        return self._request("POST","/v1/platform/deployments",json={
            "model_id":model_id,"name":name,"environment":environment,"replicas":replicas
        })

    def status(self, name, environment):
        return self._request("GET",f"/v1/platform/deployments/{name}",
                             params={"environment":environment})

    def history(self, name, environment):
        return self._request("GET",f"/v1/platform/deployments/{name}/history",
                             params={"environment":environment})

    def rollback(self, name, environment, reason):
        return self._request("POST",f"/v1/platform/deployments/{name}/rollback",
                             params={"environment":environment},json={"reason":reason})

    def train_model(self, *, name, image, dataset_uri, environment="stage",
                    workers=1, gpu_per_worker=0):
        return self._request("POST","/v1/platform/training-jobs",json={
            "name":name,"image":image,"dataset_uri":dataset_uri,
            "environment":environment,"workers":workers,
            "gpu_per_worker":gpu_per_worker
        })

    def training_status(self, job_id):
        return self._request("GET",f"/v1/platform/training-jobs/{job_id}")

    def predict(self, name, payload, environment="production"):
        return self._request("POST",f"/v1/platform/inference/{name}",
                             params={"environment":environment},json=payload)

    def close(self):
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
