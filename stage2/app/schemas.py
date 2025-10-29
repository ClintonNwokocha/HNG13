"""
Ensure data integrity and provides automatic documentation
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class CountryBase(BaseModel):
	name: str = Field(..., min_length=1, max_length=100)
	capital: Optional[str] = Field(None, max_length=100)
	region: Optional[str] = Field(None, max_length=100)
	population: int = Field(..., ge=0)
	currency_code: Optional[str] = Field(None, max_length=10)
	exchange_rate: Optional[float] = Field(None, ge=0)
	estimated_gdp: Optional[float] = Field(None, ge=0)

class CountryCreate(CountryBase):
	pass

class CountryUpdate(CountryBase):
	pass

class CountryResponse(CountryBase):

	id: int
	last_refreshed_at: datetime

	class Config:
		from_attributes = True


class RefreshResponse(BaseModel):
	message: str
	countries_processed: int
	countries_updated: int
	countries_created: int
	timestamp: datetime

class StatusResponse(BaseModel):
	total_countries: int
	last_refreshed_at: Optional[datetime]

class ErrorResponse(BaseModel):
	error: str
	details: Optional[str] = None







