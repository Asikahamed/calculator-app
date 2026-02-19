from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class OperationType(str, Enum):
    add      = "add"
    subtract = "subtract"
    multiply = "multiply"
    divide   = "divide"
    power    = "power"
    modulo   = "modulo"


# ── Request ───────────────────────────────────────────────
class CalculationRequest(BaseModel):
    operation: OperationType
    a: float
    b: float

    @field_validator("a", "b")
    @classmethod
    def must_be_finite(cls, v: float) -> float:
        import math
        if math.isnan(v) or math.isinf(v):
            raise ValueError("Value must be a finite number")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "operation": "add",
                "a": 10,
                "b": 5,
            }
        }
    }


# ── Response ──────────────────────────────────────────────
class CalculationResponse(BaseModel):
    id:         str
    operation:  str
    a:          float
    b:          float
    result:     float
    timestamp:  datetime


class HistoryResponse(BaseModel):
    total:   int
    records: list[CalculationResponse]


class HealthResponse(BaseModel):
    status:          str
    version:         str
    total_calculations: int


class ErrorResponse(BaseModel):
    detail:    str
    operation: Optional[str] = None
