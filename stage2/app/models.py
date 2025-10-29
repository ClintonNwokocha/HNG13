"""
Define database tables structure
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.database import Base


class Country(Base):

	__tablename__ = "countries"

	# Primary key
	id = Column(Integer, primary_key=True, index=True, autoincrement=True)

	# Country Information
	name = Column(String(100), unique=True, nullable=False, index=True)
	capital = Column(String(100), nullable=True)
	region = Column(String(100), nullable=True, index=True)
	population = Column(Integer, nullable=False)

	# Currency information
	currency_code = Column(String(10), nullable=True, index=True)
	exchange_rate = Column(Float, nullable=True)
	estimated_gdp = Column(Float, nullable=True)

	# Additional data
	flag_url = Column(String(255), nullable=True)

	# Timestamps
	last_refreshed_at = Column(
		DateTime(timezone=True),
		server_default=func.now(),
		onupdate=func.now(),
		nullable=False
)

	def __repr__(self):
		return f"<Country(name='{self.name}', region='{self.region}', currency='{self.currency_code}')>"


class RefreshMetadata(Base):

	__tablename__ = "refresh_metadata"

	id = Column(Integer, primary_key=True)
	total_countries = Column(Integer, default=0)
	last_refreshed_at = Column(
		DateTime(timezone=True),
		server_default=func.now()
)

	def __repr__(self):
		return f"<total={self.total_countries}, last_refresh='{self.last_refreshed_at}'>"
