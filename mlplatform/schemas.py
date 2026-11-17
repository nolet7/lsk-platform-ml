"""Versioned API contracts for deploying approved ML inference containers."""
from typing import Literal
from pydantic import BaseModel, Field

class ModelRegistration(BaseModel):
    name: str = Field(pattern=r"^[a-z][a-z0-9-]{1,39}$")
    version: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}$")
    image: str = Field(min_length=100, max_length=350)
    # A signed evaluation report and model lineage must be supplied externally.
    evaluation_reference: str = Field(min_length=8, max_length=1000)
    source_run_id: str = Field(min_length=1, max_length=256)
    model_artifact_uri: str = Field(min_length=1, max_length=1000)

class Approval(BaseModel):
    reason: str = Field(min_length=10, max_length=1000)

class DeploymentRequest(BaseModel):
    model_id: str
    name: str = Field(pattern=r"^[a-z][a-z0-9-]{1,39}$")
    environment: Literal["stage", "production"]
    replicas: int = Field(ge=2, le=10)

class RollbackRequest(BaseModel):
    reason: str = Field(min_length=10, max_length=1000)
