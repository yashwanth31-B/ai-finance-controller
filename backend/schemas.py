from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RootInfoResponse(BaseModel):
    name: str
    status: str

class HealthStatusResponse(BaseModel):
    status: str

class SystemMetricPlaceholder(BaseModel):
    match_rate: float = 0.0
    verified_accuracy: float = 0.0
    throughput: float = 0.0
    unresolved_exceptions: int = 0
