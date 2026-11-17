"""Example Ray CPU training workload using a tenant-scoped S3 CSV dataset.

Entrypoint contract: python -m lsk_training.entrypoint.
Publishes MLflow run + evaluation lineage; does not deploy an inference model.
GPU scheduling is supported by platform but this example trains on CPU.
"""
import hashlib
import io
import os
import re
from urllib.parse import urlparse


def dataset_location(uri: str, tenant: str, approved_bucket: str):
    parsed=urlparse(uri)
    prefix=f"{tenant}/datasets/"
    key=parsed.path.lstrip("/")
    if parsed.scheme!="s3" or parsed.netloc!=approved_bucket:
        raise ValueError("dataset must use approved S3 bucket")
    if not key.startswith(prefix) or not key[len(prefix):]:
        raise ValueError("dataset must live in tenant-specific dataset prefix")
    if ".." in key.split("/") or not re.fullmatch(r"[A-Za-z0-9._/-]+",key):
        raise ValueError("invalid dataset object key")
    return approved_bucket,key


def run():
    import boto3
    import mlflow
    import mlflow.sklearn
    import pandas as pd
    import ray
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import roc_auc_score
    from sklearn.model_selection import train_test_split

    tenant=os.environ["LSK_TENANT_ID"]
    name=os.environ["LSK_MODEL_NAME"]
    eval_ref=os.environ["LSK_EVALUATION_REF"]
    uri=os.environ["LSK_DATASET_URI"]
    bucket,key=dataset_location(uri,tenant,os.environ["TRAINING_DATASET_BUCKET"])
    sha=os.environ.get("SOURCE_GIT_SHA","")
    if not re.fullmatch(r"[0-9a-f]{40}",sha):
        raise RuntimeError("training image requires source git SHA build attestation")
    response=boto3.client("s3").get_object(Bucket=bucket,Key=key)
    content=response["Body"].read(32*1024*1024+1)
    if len(content)>32*1024*1024:
        raise ValueError("training input exceeds 32 MiB example limit")
    dataset_sha=hashlib.sha256(content).hexdigest()
    frame=pd.read_csv(io.BytesIO(content))
    if "target" not in frame or frame.isna().any().any():
        raise ValueError("training CSV needs target column and no missing values")
    y=frame["target"]
    X=frame.drop(columns=["target"])
    if X.empty or y.nunique()!=2 or not set(y.unique()).issubset({0,1}):
        raise ValueError("example requires numeric features and binary target")
    X=X.astype("float64")
    X_train,X_valid,y_train,y_valid=train_test_split(
        X,y,test_size=0.25,stratify=y,random_state=42)

    ray.init(address="auto",ignore_reinit_error=True)
    @ray.remote
    def score_model(depth):
        model=RandomForestClassifier(n_estimators=60,max_depth=depth,
                                     random_state=42,n_jobs=1)
        model.fit(X_train,y_train)
        return depth,float(roc_auc_score(y_valid,model.predict_proba(X_valid)[:,1]))
    results=ray.get([score_model.remote(d) for d in [4,8,None]])
    depth,metric=max(results,key=lambda item:item[1])
    final=RandomForestClassifier(n_estimators=60,max_depth=depth,random_state=42,n_jobs=1)
    final.fit(X_train,y_train)

    mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
    with mlflow.start_run() as active:
        mlflow.set_tags({
            "tenant_id":tenant,
            "model_name":name,
            "evaluation_ref":eval_ref,
            "dataset_sha256":dataset_sha,
            "git_sha":sha,
            "training_job_id":os.environ["LSK_TRAINING_JOB_ID"],
        })
        mlflow.log_param("max_depth",str(depth))
        mlflow.log_metric("validation_auc",metric)
        mlflow.sklearn.log_model(sk_model=final,artifact_path="model")
        print(f"MLflow run: {active.info.run_id}; AUC: {metric:.4f}")
    ray.shutdown()


if __name__=="__main__":
    run()
