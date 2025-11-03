from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class EarthquakeFilter(BaseModel):
	min_magnitude: Optional[float] = Field(default=4.5, description="Minimum earthquake magnitude")	
	max_magnitude: Optional[float] = Field(default=None, description="Maximum earthquake magnitude")
	hours_back: Optional[float] = Field(default=24, description="Hours to look back")
	location: Optional[str] = Field(default=None, description="Location filter (e.g., caelifornia, Japan)")
	limit: Optional[int] = Field(default=10, description="Maximum number of results")

class EarthquakeEvent(BaseModel):
	"""Earthquake event data"""
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
	"""Incoming message from telex"""
	message: str
	user_id: Optional[str] = None
	channel_id: Optional[str] = None

class TelexResponse(BaseModel):
	"""Response to send back to telex"""
	response: str
	events: Optional[List[EarthquakeEvent]] = None
