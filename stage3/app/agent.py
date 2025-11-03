import re
from typing import Tuple
from .models import EarthquakeFilter, TelexResponse, EarthquakeEvent
from .earthquake import EarthquakeAPIClient
from datetime import datetime

class EarthquakeAgent:
	"""AI agent for earthquake monitoring"""


	def __init__(self):
		self.api_client = EarthquakeAPIClient()

	def parse_message(self, message: str) -> EarthquakeFilter:
		"""Parse use message to extract filter criteria"""

		message_lower = message.lower()
		filters = EarthquakeFilter()

		# Parse magnitude
		mag_pattern = r'magnitude\s+(\d+\.?\d*)'
		mag_match = re.search(mag_pattern, message_lower)
		if mag_match:
			filters.min_magnitude = float(mag_match.group(1))

		# Alternative magnitude patterns
		if 'above' in message_lower or "greater than" in message_lower:
			mag_pattern2 = r'(?:above|greater than)\s+(\d+\.?\d*)'
			mag_match2 = re.search(mag_pattern2, message_lower)
			if mag_match2:
				filters.min_magnitude = float(mag_match2.group(1))

		# Parse time range
		if 'last hour' in message_lower or 'past hour' in message_lower:
			filters.hours_back = 1
		elif 'last 12 hours' in message_lower or 'past 12 hours' in message_lower:
			filters.hours_back = 12
		elif 'today' in message_lower:
			filters.hours_back = 24
		elif 'week' in message_lower:
			filters.hours_back = 168
		else:
			hours_pattern = r'(\d+)\s+hours?'
			hours_match = re.search(hours_pattern, message_lower)
			if hours_match:
				filters.hours_back = int(hours_match.group(1))

		# Parse location
		location_keywords = ['in', 'near', 'around']
		for keyword in location_keywords:
			if keyword in message_lower:
				parts = message_lower.split(keyword)
				if len(parts) > 1:
					location_text = parts[1].strip()
					location_words = location_text.split()[:3]
					filters.location = ' '.join(location_words).strip('.,!?')
					break

		# Parse limit
		limit_pattern = r'(?:show|list|get)\s+(\d+)'
		limit_match = re.search(limit_pattern, message_lower)
		if limit_match:
			filters.limit = int(limit_match.group(1))

		return filters

	def format_response(self, events: list[EarthquakeEvent], filters: EarthquakeFilter) -> str:
		"""Format earthquake data into readable reponse"""

		if not events:
			return f"No earthquakes found with magnitude {filters.min_magnitude}+ in the last {filters.hours_back} hours."

		response = f"Found {len(events)} earthquake(s) in the last {filters.hours_back} hours:\n\n"

		for i, event in enumerate(events, 1):
			tsunami_warn = " TSUNAMI WARNING " if event.tsunami else ""
			alert = f"[{event.alert_level.upper()}]" if event.alert_level else ""

			response += f"{i}. Magnitude {event.magnitude} - {event.place}\n"
			response += f" {event.time.strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
			response += f" Lat: {event.latitude:.2f}, Lon: {event.longitude:.2f}\n"
			response += f" Depth: {event.depth:.1f} km{tsunami_warn}{alert}\n"
			response += f" {event.url}\n\n"

		return response

	async def process_message(self, message: str) -> TelexResponse:
		"""Process incoming message and return response"""

		message_lower = message.lower()

		# Handle greetings
		if any(word in message_lower for word in ['hello', 'hi', 'hey']):
			return TelexResponse(
				response = "Hello! I'm your earthquake monitoring agent. I can help you track recent earthquakes worldwide. \n\n"
					"Try asking me:\n"
					". 'Show earthquakes above magnitude 5'\n"
					". 'Earthquakes in Japan in the last 24 hours'\n"
					". 'Show me the last 5 earthquakes'"
					". 'Magnitue 6+ earthquakes today'"
			)

		# Handle help requests
		if 'help' in message_lower:
			return TelexResponse(
				response = "Here's what I can do:\n\n"
					"I monitor earthquakes worldwide and can filter by:\n"
					". Magnitude (e.g., 'magnitude 5+', 'above 6.0')\n"
					". Time range (e.g., 'last hour', 'today', 'past week')\n"
					". Location (e.g., 'in California', 'near Japan')\n"
					". Number of results (e.g., 'show 5 earthquakes')\n\n"
					"Example queries:\n,"
					". 'Earthquakes above magnitude 5 in the last 24 hours'\n"
					". 'Show 10 recent earthquakes near Indonesia'\n"
					". 'Magnitude 4+ earthquakes in California today'"
			)
		# Process earthquake query
		try:
			filters = self.parse_message(message)
			events = await self.api_client.get_earthquakes(filters)
			response_text = self.format_response(events, filters)

			return TelexResponse(
				response=response_text,
				events=events
			)

		except Exception as e:
			return TelexResponse(
				response=f"Sorry, I encountered an error: {str(e)}\n"
					"Please try rephrasing your query or type 'help' for assistance."

			)

	async def close(self):
		"""Cleanup resources"""
		await self.api_client.close()
