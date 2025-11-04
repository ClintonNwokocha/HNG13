import re
from typing import List

from .models import EarthquakeFilter, TelexResponse, EarthquakeEvent
from .earthquake import EarthquakeAPIClient


class EarthquakeAgent:
    """AI agent for earthquake monitoring"""

    def __init__(self):
        self.api_client = EarthquakeAPIClient()

    def parse_message(self, message: str) -> EarthquakeFilter:
        msg = (message or "").strip()
        low = msg.lower()
        f = EarthquakeFilter()

        # Magnitude patterns
        patterns = [
            r'>=\s*([0-9]+(?:\.[0-9]+)?)',
            r'>\s*=\s*([0-9]+(?:\.[0-9]+)?)',
            r'(?:mag(?:nitude)?|m)\s*([0-9]+(?:\.[0-9]+)?)\+?',
            r'([0-9]+(?:\.[0-9]+)?)\s*\+',
            r'greater than\s*([0-9]+(?:\.[0-9]+)?)',
            r'above\s*([0-9]+(?:\.[0-9]+)?)',
        ]
        for p in patterns:
            m = re.search(p, low)
            if m:
                try:
                    f.min_magnitude = float(m.group(1))
                    break
                except ValueError:
                    pass

        # Time patterns
        mh = re.search(r'(?:last|past)\s+(\d+)\s+hours?', low)
        if mh:
            f.hours_back = int(mh.group(1))
        
        md = re.search(r'(?:last|past)\s+(\d+)\s+days?', low)
        if md:
            f.hours_back = int(md.group(1)) * 24
        
        if re.search(r'\btoday\b', low):
            f.hours_back = max(f.hours_back or 0, 24)
        
        if re.search(r'\bweek\b', low) and not md:
            f.hours_back = max(f.hours_back or 0, 7 * 24)

        # Limit
        mlimit = re.search(r'(?:show|list|get)\s+(\d+)', low)
        if mlimit:
            try:
                f.limit = int(mlimit.group(1))
            except ValueError:
                pass

        # Location
        loc = None
        mloc = re.search(r'(?:\b(in|near|around)\b)\s+([A-Za-z][A-Za-z\s\-\.,]+)$', low)
        if mloc:
            candidate = mloc.group(2).strip().strip('.,!?')
            if not re.search(r'^\s*the\s+last\s+\d+\s+(?:days?|hours?)\s*$', candidate):
                words = candidate.split()
                loc = " ".join(words[:4])
        
        if not loc:
            for kw in [" in ", " near ", " around "]:
                if kw in low:
                    part = low.rsplit(kw, 1)[-1].strip()
                    if re.match(r'^the\s+last\s+\d+\s+(?:days?|hours?)$', part):
                        continue
                    loc = " ".join(part.split()[:4]).strip('.,!?')
                    break
        
        if loc:
            f.location = loc

        return f

    def _format_response(self, events: List[EarthquakeEvent], filters: EarthquakeFilter) -> str:
        hrs = int(filters.hours_back or 24)
        period = f"last {hrs} hour{'s' if hrs != 1 else ''}"
        mag = f"{(filters.min_magnitude or 0):.1f}+"

        if not events:
            header = "No earthquakes found"
            if filters.location:
                header += f" in {filters.location}"
            header += f" in the {period} (M{mag})."
            return header

        header = f"Found {len(events)} earthquake(s)"
        if filters.location:
            header += f" in {filters.location}"
        header += f" in the {period} (M{mag}):"

        lines = [header, ""]
        for i, ev in enumerate(events, 1):
            alert = f" [{ev.alert_level.upper()}]" if ev.alert_level else ""
            tsunami = " ⚠️ TSUNAMI WARNING" if ev.tsunami else ""
            lines.append(f"{i}. M{ev.magnitude:.1f} — {ev.place}")
            lines.append(f"   {ev.time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
            lines.append(f"   Lat: {ev.latitude:.2f}, Lon: {ev.longitude:.2f} | Depth: {ev.depth:.1f} km{tsunami}{alert}")
            if ev.url:
                lines.append(f"   {ev.url}")
            lines.append("")
        return "\n".join(lines).rstrip()

    async def process_message(self, message: str) -> TelexResponse:
        low = (message or "").lower()

        if any(g in low for g in ["hello", "hi", "hey"]):
            return TelexResponse(
                response=(
                    "Hello! I monitor earthquakes worldwide.\n\n"
                    "Try:\n"
                    "• show 5 earthquakes above magnitude 5 in the last 24 hours\n"
                    "• earthquakes in Japan in the last 7 days\n"
                    "• magnitude 6+ today near Indonesia"
                )
            )

        if "help" in low:
            return TelexResponse(
                response=(
                    "I can filter by:\n"
                    "• Magnitude (e.g., '>=5', 'm5+', 'above 4.5')\n"
                    "• Time (e.g., 'last 24 hours', 'past 7 days', 'today')\n"
                    "• Location (e.g., 'in Japan', 'near California')\n"
                    "• Limit (e.g., 'show 10')\n"
                )
            )

        try:
            filters = self.parse_message(message)
            events = await self.api_client.get_earthquakes(filters)
            text = self._format_response(events, filters)
            return TelexResponse(response=text, events=events)
        except Exception as e:
            return TelexResponse(
                response=(
                    f"Sorry, something went wrong: {e}\n"
                    "Please try again or type 'help'."
                )
            )

    async def close(self):
        await self.api_client.close()