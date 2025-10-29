"""
Fetches data from restcountries.com and exchange rate API
"""

import httpx
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

COUNTRIES_API_URL = os.getenv("COUNTRIES_API_URL", "https://restcountries.com/v3.1/all")
EXCHANGE_API_URL = os.getenv("EXCHANGE_API_URL", "https://open.er-api.com/v6/latest/USD")

TIMEOUT = 30.0

async def fetch_countries() -> List[Dict]:
	"""
	Fetch all countries from REST Countries API
	
	Returns:
		List of country dictionaries
		
	Raises:
		Exception: If the API request fails
	"""
	if not COUNTRIES_API_URL:
		raise Exception("COUNTRIES_API_URL environment variable not set")
	
	async with httpx.AsyncClient(timeout=TIMEOUT) as client:
		try:
			response = await client.get(COUNTRIES_API_URL)
			response.raise_for_status()
			data = response.json()
			
			# Validate response
			if not isinstance(data, list):
				raise Exception(f"Expected list from countries API, got {type(data)}")
			
			return data
			
		except httpx.TimeoutException:
			raise Exception(f"Timeout while fetching countries from {COUNTRIES_API_URL}")
		except httpx.HTTPStatusError as e:
			raise Exception(f"HTTP {e.response.status_code} error fetching countries: {str(e)}")
		except httpx.HTTPError as e:
			raise Exception(f"HTTP error fetching countries: {str(e)}")
		except Exception as e:
			raise Exception(f"Unexpected error fetching countries: {str(e)}")


async def fetch_exchange_rates() -> Dict[str, float]:
	"""
	Fetch exchange rates from Exchange Rate API
	
	Returns:
		Dictionary of currency codes to exchange rates
		
	Raises:
		Exception: If the API request fails
	"""
	if not EXCHANGE_API_URL:
		raise Exception("EXCHANGE_API_URL environment variable not set")
	
	async with httpx.AsyncClient(timeout=TIMEOUT) as client:
		try:
			response = await client.get(EXCHANGE_API_URL)
			response.raise_for_status()
			data = response.json()
			
			# Validate response structure
			if not isinstance(data, dict):
				raise Exception(f"Expected dict from exchange API, got {type(data)}")
			
			if "rates" not in data:
				raise Exception("No 'rates' key in exchange rate response")
			
			rates = data["rates"]
			
			if not isinstance(rates, dict):
				raise Exception(f"Expected dict for rates, got {type(rates)}")
			
			return rates
			
		except httpx.TimeoutException:
			raise Exception(f"Timeout while fetching exchange rates from {EXCHANGE_API_URL}")
		except httpx.HTTPStatusError as e:
			raise Exception(f"HTTP {e.response.status_code} error fetching exchange rates: {str(e)}")
		except httpx.HTTPError as e:
			raise Exception(f"HTTP error fetching exchange rates: {str(e)}")
		except Exception as e:
			raise Exception(f"Unexpected error fetching exchange rates: {str(e)}")

