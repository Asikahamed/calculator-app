import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Path
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from .calculator import OPERATIONS
from app.schemas import (
    CalculationRequest,
    CalculationResponse,
    HealthResponse,
    HistoryResponse,
    ErrorResponse,
)
from .store import store

# ── App setup ─────────────────────────────────────────────
app = FastAPI(
    title="Calculator API",
    description="Simple calculator API built for DevOps learning — CI/CD, Docker, GCP.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Exposes /metrics endpoint for Prometheus scraping
Instrumentator().instrument(app).expose(app)


# ── Routes ────────────────────────────────────────────────

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health check",
)
def health():
    """Used by Cloud Run and GKE liveness/readiness probes."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        total_calculations=store.count(),
    )


@app.post(
    "/calculate",
    response_model=CalculationResponse,
    status_code=201,
    tags=["Calculator"],
    summary="Perform a calculation",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input or math error"},
    },
)
def calculate(payload: CalculationRequest):
    """
    Perform one of the supported operations:
    `add`, `subtract`, `multiply`, `divide`, `power`, `modulo`
    """
    operation_fn = OPERATIONS[payload.operation]

    try:
        result = operation_fn(payload.a, payload.b)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    record = CalculationResponse(
        id=str(uuid.uuid4()),
        operation=payload.operation,
        a=payload.a,
        b=payload.b,
        result=result,
        timestamp=datetime.now(timezone.utc),
    )

    store.save(record)
    return record


@app.get(
    "/history",
    response_model=HistoryResponse,
    tags=["Calculator"],
    summary="Get calculation history",
)
def get_history():
    """Returns all past calculations, most recent first."""
    records = store.get_all()
    return HistoryResponse(total=len(records), records=records)


@app.get(
    "/history/{record_id}",
    response_model=CalculationResponse,
    tags=["Calculator"],
    summary="Get a specific calculation by ID",
    responses={
        404: {"model": ErrorResponse, "description": "Record not found"},
    },
)
def get_calculation(
    record_id: str = Path(..., description="UUID of the calculation record"),
):
    record = store.get(record_id)
    if not record:
        raise HTTPException(
            status_code=404,
            detail=f"Calculation with id '{record_id}' not found",
        )
    return record


@app.delete(
    "/history",
    status_code=204,
    tags=["Calculator"],
    summary="Clear all calculation history",
)
def clear_history():
    """Wipes the in-memory store. Useful for testing."""
    store.clear()
    return JSONResponse(status_code=204, content=None)


# ── Global exception handler ──────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"},
    )
