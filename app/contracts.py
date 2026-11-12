from pydantic import BaseModel, Field

class Signals(BaseModel):
    surface_texture: float = Field(ge=0, le=1)
    edge_irregularity: float = Field(ge=0, le=1)
    color_variance: float = Field(ge=0, le=1)

class PredictRequest(BaseModel):
    inspection_id: str
    signals: Signals

class ReviewRequest(BaseModel):
    inspection_id: str
    disposition: str
    rationale: str = Field(min_length=8)
    prediction_id: str
