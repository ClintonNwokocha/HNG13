import httpx
from datetime import datetime, timedelta
from typing import List, Optional
from .models import EarthquakeEvent, EarthquakeFilter

class EarthquakeAPIClient:
	"""Client for USGS Earthquake API"""

	BASE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

	def __init__(self):
		self.client = httpx.AsyncClient(timeout=30.0)

	async def get_earthquakes(self, filters: EarthquakeFilter) -> List[EarthquakeEvent]:
		"""Fetch earthquakes based on filter criteria"""

		# Calculate time range
		end_time = datetime.utcnow()
		start_time = end_time - timedelta(hours=filters.hours_back)


		# build query params
		params = {
			"format": "geojson",
			"starttime": start_time.isoformat(),
			"endtime": end_time.isoformat(),
			"minmagnitude": filters.min_magnitude,
			"orderby": "magnitude",
			"limit": filters.limit
		}

		if filters.max_magnitude:
			params["maxmagnitude"] = filters.max_magnitude

		try:
			response = await self.client.get(self.BASE_URL, params=params)
			response.raise_for_status()
			data = response.json()

			events = []
			for feature in data.get("features", []):
				props = feature["properties"]
				coords = feature["geometry"]["coordinates"]

				# Filter by location if specified
				if filters.location:
					place = props.get("place", "").lower()
					if filters.location.lower() not in place:
						continue

				event = EarthquakeEvent(
					id=feature["id"],
					magnitude=props.get("mag", 0),
					place=props.get("place", "Unknown location"),
					time=datetime.fromtimestamp(props.get("time", 0) / 1000),
					latitude=coords[1],
					longitude=coords[0],
					depth=coords[2],
					url=props.get("url", ""),
					alert_level=props.get("alert"),
					tsunami=props.get("tsunami", 0) == 1
				)
				events.append(event)

			return events

		except httpx.HTTPError as e:
			print(f"Error fetching earthquakes: {e}")
			return []

	async def close(self):
		"""Close the HTTP client"""
		await self.client.aclose()
