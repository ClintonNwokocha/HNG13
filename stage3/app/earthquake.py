import httpx
from datetime import datetime, timedelta, timezone
from typing import List, Dict
from .models import EarthquakeEvent, EarthquakeFilter

class EarthquakeAPIClient:
    BASE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_earthquakes(self, filters: EarthquakeFilter) -> List[EarthquakeEvent]:
        now = datetime.now(timezone.utc)
        start = now - timedelta(hours=int(filters.hours_back or 24))

        params: Dict[str, str] = {
            "format": "geojson",
            "starttime": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "endtime": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "minmagnitude": f"{filters.min_magnitude or 0}",
            "orderby": "time",
            "limit": f"{min(max(filters.limit or 10, 1), 200)}",
        }
        if filters.max_magnitude is not None:
            params["maxmagnitude"] = f"{filters.max_magnitude}"

        print("[USGS] Query params =>", params, flush=True)

        try:
            resp = await self.client.get(self.BASE_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as e:
            print(f"[USGS] HTTP error: {e}", flush=True)
            return []

        events: List[EarthquakeEvent] = []
        loc = (filters.location or "").lower().strip() or None

        for feat in data.get("features", []):
            props = feat.get("properties") or {}
            geom = feat.get("geometry") or {}
            coords = (geom.get("coordinates") or [None, None, None])

            if loc:
                place_text = (props.get("place") or "").lower()
                if loc not in place_text:
                    continue

            try:
                events.append(
                    EarthquakeEvent(
                        id=feat.get("id", ""),
                        magnitude=props.get("mag") or 0.0,
                        place=props.get("place") or "Unknown location",
                        time=datetime.fromtimestamp((props.get("time") or 0)/1000, tz=timezone.utc),
                        latitude=float(coords[1]),
                        longitude=float(coords[0]),
                        depth=float(coords[2]),
                        url=props.get("url") or "",
                        alert_level=props.get("alert"),
                        tsunami=(props.get("tsunami") == 1),
                    )
                )
            except Exception as e:
                print(f"[USGS] Skip malformed feature: {e}", flush=True)
                continue

        return events

    async def close(self):
        await self.client.aclose()