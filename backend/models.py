"""
SQLAlchemy models for ContextIQ AI - Phase 1
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def generate_uuid() -> str:
    return str(uuid.uuid4())


class OperationStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OperationPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class OperationalRecord(Base):
    __tablename__ = "operational_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    status = Column(Enum(OperationStatus), nullable=False, default=OperationStatus.OPEN)
    priority = Column(Enum(OperationPriority), nullable=False, default=OperationPriority.MEDIUM)

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    external_data_snapshots = relationship(
        "ExternalDataSnapshot", back_populates="operation", cascade="all, delete-orphan"
    )
    risk_events = relationship(
        "RiskEvent", back_populates="operation", cascade="all, delete-orphan"
    )


class ExternalDataSnapshot(Base):
    __tablename__ = "external_data_snapshots"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    operation_id = Column(String(36), ForeignKey("operational_records.id"), nullable=False, index=True)

    source = Column(String(100), nullable=False)
    raw_payload = Column(Text, nullable=False)
    fetched_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    operation = relationship("OperationalRecord", back_populates="external_data_snapshots")


class RiskEvent(Base):
    __tablename__ = "risk_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    operation_id = Column(String(36), ForeignKey("operational_records.id"), nullable=False, index=True)

    risk_level = Column(Enum(RiskLevel), nullable=False)
    risk_score = Column(Float, nullable=False)
    contributing_factors = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    operation = relationship("OperationalRecord", back_populates="risk_events")
    intervention_outcomes = relationship(
        "InterventionOutcome", back_populates="risk_event", cascade="all, delete-orphan"
    )


class InterventionOutcome(Base):
    __tablename__ = "intervention_outcomes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    risk_event_id = Column(String(36), ForeignKey("risk_events.id"), nullable=False, index=True)

    predicted_outcome = Column(Text, nullable=False)
    operator_action = Column(Text, nullable=True)
    actual_outcome = Column(Text, nullable=True)

    recorded_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    risk_event = relationship("RiskEvent", back_populates="intervention_outcomes")
