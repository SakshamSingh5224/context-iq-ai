"""
FastAPI application for ContextIQ AI.
"""

import json
import os
from typing import Generator, List

try:  # optional: load backend/.env when running locally
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from models import Base, OperationalRecord, RiskEvent
from schemas import OperationCreate, OperationResponse, RiskEventResponse
from services.external_data import get_weather
from services.risk_engine import (
    compute_risk_score,
    derive_internal_risk_from_priority,
    derive_external_risk_from_weather,
)
from services.copilot import generate_intervention_strategy

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./contextiq.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(title="ContextIQ AI API", version="0.1.0")

# --- CORS (Phase 4: local origins only; Phase 5 makes this env-driven) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "ContextIQ AI API is operational. Visit /docs for OpenAPI documentation."}


@app.post(
    "/api/v1/operations",
    response_model=OperationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["operations"],
)
def create_operation(
    payload: OperationCreate, db: Session = Depends(get_db)
) -> OperationalRecord:
    try:
        record = OperationalRecord(**payload.model_dump())
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create operational record: {exc}",
        ) from exc


@app.post(
    "/api/v1/operations/{operation_id}/assess",
    tags=["operations"],
)
async def assess_operation_risk(
    operation_id: str, db: Session = Depends(get_db)
) -> dict:
    # 1. Fetch the operation from the database
    operation = db.query(OperationalRecord).filter(OperationalRecord.id == operation_id).first()
    if not operation:
        raise HTTPException(status_code=404, detail="Operation not found")

    # 2. Fetch external weather data if location is provided
    weather_data = {}
    external_risk = 0.0
    if operation.latitude is not None and operation.longitude is not None:
        try:
            weather_data = await get_weather(operation.latitude, operation.longitude)
            external_risk = derive_external_risk_from_weather(weather_data)
        except Exception as exc:
            print(f"Warning: Failed to fetch weather data - {exc}")

    # 3. Calculate Deterministic Risk
    internal_risk = derive_internal_risk_from_priority(operation.priority)

    risk_result = compute_risk_score(
        internal_risk=internal_risk,
        external_risk=external_risk,
        time_pressure=0.5,     # Static placeholder for now
        historical_risk=0.2    # Static placeholder for now
    )

    # 4. Persist the assessment so it shows up in risk history
    risk_event = RiskEvent(
        operation_id=operation.id,
        risk_level=risk_result.risk_level,
        risk_score=risk_result.risk_score,
        contributing_factors=json.dumps(risk_result.breakdown),
    )
    db.add(risk_event)
    db.commit()

    # 5. Generate AI Copilot Strategy
    try:
        strategy = generate_intervention_strategy(
            operation_title=operation.title,
            risk_level=risk_result.risk_level.value,
            weather_summary=weather_data
        )
    except Exception as exc:
        strategy = f"AI strategy generation currently unavailable: {exc}"

    # 6. Return the full assessment
    return {
        "operation_id": operation.id,
        "title": operation.title,
        "risk_assessment": {
            "score": risk_result.risk_score,
            "level": risk_result.risk_level,
            "breakdown": risk_result.breakdown
        },
        "copilot_strategy": strategy
    }


@app.get(
    "/api/v1/risk-events",
    response_model=List[RiskEventResponse],
    tags=["risk"],
)
def list_risk_events(limit: int = 50, db: Session = Depends(get_db)):
    return (
        db.query(RiskEvent)
        .order_by(RiskEvent.created_at.desc())
        .limit(min(max(limit, 1), 200))
        .all()
    )


@app.get(
    "/api/v1/operations/{operation_id}/risk-history",
    response_model=List[RiskEventResponse],
    tags=["risk"],
)
def get_risk_history(operation_id: str, db: Session = Depends(get_db)):
    operation = db.query(OperationalRecord).filter(OperationalRecord.id == operation_id).first()
    if not operation:
        raise HTTPException(status_code=404, detail="Operation not found")
    return (
        db.query(RiskEvent)
        .filter(RiskEvent.operation_id == operation_id)
        .order_by(RiskEvent.created_at.desc())
        .all()
    )
