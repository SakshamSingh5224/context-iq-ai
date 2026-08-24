"""
FastAPI boilerplate for Phase 1.
"""

from typing import Generator

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from models import Base, OperationalRecord
from schemas import OperationCreate, OperationResponse

SQLALCHEMY_DATABASE_URL = "sqlite:///./contextiq.db"

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
