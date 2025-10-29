"""
Business logic for country data management
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models
from typing import List, Optional
import random
from datetime import datetime

def get_country_by_name(db: Session, name: str) -> Optional[models.Country]:
	"""
	Get a country by name

	Args:
		db: Database session
		name: Country name

	Returns:
		Country object or None
	"""
	return db.query(models.Country).filter(func.lower(models.Country.name) == func.lower(name)).first()

def get_all_countries(
	db: Session,
	region: Optional[str] = None,
	currency: Optional[str] = None,
	sort: Optional[str] = None
) -> List[models.Country]:
	"""
	Get all countries with optional filtering and sorting.

	Args:
		db: Database session
		region: Filter by region (e.g., "Africa")
		currency: Filter by currency code (e.g., "NGN")
		sort: Sort order - "gdp_desc", "gdp_asc", "population_desc", "population_asc"

	Returns:
		List of Country objects
	"""
	query = db.query(models.Country)

	# Apply filter
	if region:
		query = query.filter(func.lower(models.Country.region) == func.lower(region))

	if currency:
		query = query.filter(func.lower(models.Country.currency_code) == func.lower(currency))

	# Apply sorting
	if sort == "gdp_desc":
		query = query.order_by(models.Country.estimated_gdp.desc())
	elif sort == "gdp_asc":
		query = query.order_by(models.Country.estimated_gdp.asc())
	elif sort == "population_desc":
		query = query.order_by(models.Country.population.desc())
	elif sort == "population_asc":
		query = query.order_by(models.Country.population.asc())
	else:
		query = query.order_by(models.Country.name)

	return query.all()

def create_or_update_country(
	db: Session,
	country_data: dict,
	exchange_rates: dict
) -> tuple[models.Country, bool]:
	"""
	Create nw country or update existig one

	Args:
		db: Database session
		country_data: Country data from external API
		exchange_rates: Dictionary of exchange rates

	Returns:
		Tuple of (Country object, was_created: bool)
	"""

	# Extract name (REST Countries v3 format)
	name_data = country_data.get("name", {})
	if isinstance(name_data, dict):
		name = name_data.get("common")
	
	else:
		name = country_data.get("name")
	
	if not name:
		return None, False
	
	# Check if country exists
	existing = get_country_by_name(db, name)

	# Extract currency code
	currencies = country_data.get("currencies", {})
	currency_code = None

	if isinstance(currencies, list) and len(currencies) > 0:

		first_currency = currencies[0]
		if isinstance(first_currency, dict):
			currency_code = first_currency.get('code')
	elif isinstance(currencies, dict) and currencies:
		currency_code = list(currencies.key())[0]

	exchange_rate = None
	estimated_gdp = None

	if currency_code and currency_code in exchange_rates:
		exchange_rate = exchange_rates[currency_code]


		# Calculate estimated GDP
		population = country_data.get("population", 0)
		if population > 0 and exchange_rate >0:
			random_multiplier = random.uniform(1000, 2000)
			estimated_gdp = (population * random_multiplier) / exchange_rate
	elif not currency_code:
		estimated_gdp = 0.0


	# Extract capital
	capital_data = country_data.get("capital", [])
	if isinstance(capital_data, str):
		capital = capital_data
	elif isinstance(capital_data, list) and len(capital_data) > 0:
		capital = capital_data[0]

	else:
		capital = None

	# Extract flag URL
	flags_data = country_data.get("flags", {})
	flag_url = flags_data.get("png") or flags_data.get("svg")


	# Prepare country data
	country_dict = {
		"name": name,
		"capital": capital,
		"region": country_data.get("region"),
		"population": country_data.get("population", 0),
		"currency_code": currency_code,
		"exchange_rate": exchange_rate,
		"estimated_gdp": estimated_gdp,
		"flag_url": flag_url,
		"last_refreshed_at": datetime.utcnow()
	}

	if existing:
		# Update existing country
		for key, value in country_dict.items():
			setattr(existing, key, value)
		db.commit()
		db.refresh(existing)
		return existing, False
	else:
		# Create new country
		new_country = models.Country(**country_dict)
		db.add(new_country)
		db.commit()
		db.refresh(new_country)
		return new_country, True
	
def delete_country(db: Session, name: str) -> bool:
	"""
	Delete a country by name

	Args:
		db: Database session
		name: Country name

	Returns:
		True if deleted, False if not found
	"""

	country = get_country_by_name(db, name)
	if country:
		db.delete(country)
		db.commit()
		return True
	return False


def get_or_create_metadata(db: Session) -> models.RefreshMetadata:
	"""
	Get or create refresh metadata record

	Args:
		db: Database session

	Returns:
		RefreshMetadata object
	"""

	metadata = db.query(models.RefreshMetadata).first()
	if not metadata:
		metadata = models.RefreshMetadata(total_countries=0)
		db.add(metadata)
		db.commit()
		db.refresh(metadata)
	return metadata

def update_metadata(db: Session, total_countries: int):
	"""
	Update refresh metadata.

	Args:
		db: Database session
		total_countries: Total number of countries in database
	"""
	metadata = get_or_create_metadata(db)
	metadata.total_countries = total_countries
	metadata.last_refreshed_at = datetime.utcnow()
	db.commit()

def get_top_countries_by_gdp(db: Session, limit: int = 5) -> List[models.Country]:
	"""
	Get top countries by estimated GDP.

	Args:
		db: Database session
		limit: Number of countries to return

	Returns:
		List of Country objects
	"""

	return db.query(models.Country).filter(models.Country.estimated_gdp.isnot(None)).order_by(models.Country.estimated_gdp.desc()).limit(limit).all()