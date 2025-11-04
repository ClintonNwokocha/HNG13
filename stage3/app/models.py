from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class A2AResponse(BaseModel):
    response: str
    conversationId: Optional[str] = None
    metadata: Optional[dict] = None


class EarthquakeFilter(BaseModel):
    min_magnitude: Optional[float] = Field(default=4.5, description="Minimum magnitude")
    max_magnitude: Optional[float] = Field(default=None, description="Maximum magnitude")
    hours_back: Optional[int] = Field(default=24, description="Hours to look back")
    location: Optional[str] = Field(default=None, description="Location filter (e.g., Japan)")
    limit: Optional[int] = Field(default=10, description="Max results (1–200)")


class EarthquakeEvent(BaseModel):
    id: str
    magnitude: float
    place: str
    time: datetime
    latitude: float
    longitude: float
    depth: float
    url: str
    alert_level: Optional[str] = None
    tsunami: bool = False


class TelexMessage(BaseModel):
    message: str
    user_id: Optional[str] = None
    channel_id: Optional[str] = None


class TelexResponse(BaseModel):
    response: str
    events: Optional[List[EarthquakeEvent]] = None
