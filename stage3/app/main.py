from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Any, Dict, Optional

from .agent import EarthquakeAgent
from .models import A2AResponse

app = FastAPI(
    title="Earthquake Monitoring Agent",
    description="Real-time global earthquake monitoring agent for Telex.im",
    version="1.0.0",
)

# CORS: allow Telex.* and local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "https://app.telex.im", "https://*.telex.im"],
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS", "GET"],
    allow_headers=["*"],
)

agent = EarthquakeAgent()


def extract_text_from_request(data: Dict[str, Any]) -> Optional[str]:
    """
    Extract text from common A2A payload shapes:
    - {text|message|prompt|input|query: "..."}
    - {"params": {"message": {"parts":[{"kind":"text","text":"..."}]}}}
    """
    # Simple keys first
    for key in ("text", "message", "prompt", "input", "query"):
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()

    # JSON-RPC-ish format (Telex style)
    params = data.get("params")
    if isinstance(params, dict):
        msg = params.get("message")
        if isinstance(msg, dict):
            parts = msg.get("parts")
            if isinstance(parts, list):
                for part in parts:
                    if isinstance(part, dict) and part.get("kind") == "text":
                        t = (part.get("text") or "").strip()
                        if t:
                            return t

    return None


@app.get("/health")
async def health():
    return {"status": "ok", "ts": datetime.utcnow().isoformat() + "Z"}


@app.post("/a2a/agent/earthquake")
async def telex_handler(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    text = extract_text_from_request(body) or "recent"

    # Use the async processing entrypoint
    result = await agent.process_message(text)

    # Telex-friendly envelope
    return A2AResponse(
        response=result.response,
        conversationId=body.get("conversationId"),
        metadata={"count": len(result.events or [])},
    ).dict()


@app.on_event("shutdown")
async def shutdown_event():
    # Close the httpx client cleanly
    await agent.close()
