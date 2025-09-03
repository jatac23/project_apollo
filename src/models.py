"""Data models for the Apollo labeling pipeline."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AddressLabel(BaseModel):
    """Standardized address label model."""

    address: str
    label: str
    confidence: float
    created_at: datetime
    updated_at: datetime
    source_rule: str

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class LabelCandidate(BaseModel):
    """Label candidate for processing."""

    address: str
    label: str
    confidence: float
    source_rule: str
    as_of_date: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
