"""
Pydantic schemas for the OperationalRecord entity.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from models import OperationPriority, OperationStatus


class OperationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=5000)
    status: OperationStatus = OperationStatus.OPEN
    priority: OperationPriority = OperationPriority.MEDIUM
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)

    @model_validator(mode="after")
    def validate_location_pair(self) -> "OperationBase":
        has_lat = self.latitude is not None
        has_lon = self.longitude is not None
        if has_lat != has_lon:
            raise ValueError(
                "Both latitude and longitude must be provided together, or omitted."
            )
        return self


class OperationCreate(OperationBase):
    pass


class OperationUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=5000)
    status: Optional[OperationStatus] = None
    priority: Optional[OperationPriority] = None
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)


class OperationResponse(OperationBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
