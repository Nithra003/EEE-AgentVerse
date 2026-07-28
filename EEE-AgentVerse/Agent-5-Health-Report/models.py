from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field


class HealthMetricStatus(str, Enum):
    NORMAL = "Normal"
    HIGH = "High"
    LOW = "Low"
    FEVER = "Fever"
    CRITICAL = "Critical"
    FAIR = "Fair"
    POOR = "Poor"
    ACTIVE = "Active"
    LOW_ACTIVITY = "Low Activity"


class HealthData(BaseModel):
    patient_name: str = Field(..., description="Patient full name")
    age: int = Field(..., ge=0, description="Patient age in years")
    heart_rate: int = Field(..., ge=0, description="Heart rate in beats per minute")
    spo2: int = Field(..., ge=0, le=100, description="Oxygen saturation percentage")
    body_temperature: float = Field(..., description="Body temperature in Celsius")
    blood_pressure: str = Field(..., description="Systolic/diastolic blood pressure")
    steps: int = Field(..., ge=0, description="Daily steps count")
    sleep_hours: float = Field(..., ge=0, description="Total sleep hours")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of the health reading")
    source: str = Field(default="wearable-device", description="Origin of the data")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Optional metadata for routing")


class HealthReport(BaseModel):
    report_id: str = Field(default_factory=lambda: f"HR-{uuid.uuid4().hex[:8].upper()}")
    patient_name: str
    age: int
    timestamp: datetime
    metrics: Dict[str, str]
    analysis: Dict[str, str]
    overall_status: str
    risk_level: str
    recommendations: List[str]
    summary: str
    source: str = Field(default="Health Report Agent")


class MessageEnvelope(BaseModel):
    type: str
    payload: dict
    created_at: datetime = Field(default_factory=datetime.utcnow)
