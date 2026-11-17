# Example only: verify base image digest, scan, sign and publish immutable ECR digest.
# Ray runtime version must match platform RAY_RUNTIME_VERSION.
FROM rayproject/ray:2.52.0
ARG SOURCE_GIT_SHA
ENV SOURCE_GIT_SHA=${SOURCE_GIT_SHA} PYTHONPATH=/opt/training HOME=/tmp
USER root
RUN python -m pip install --no-cache-dir "boto3>=1.35,<2" "mlflow>=3,<4" "pandas>=2.2,<4" "scikit-learn>=1.5,<2"
COPY examples/ray_training/lsk_training /opt/training/lsk_training
RUN chmod -R a+rX /opt/training
USER 10001
WORKDIR /opt/training
