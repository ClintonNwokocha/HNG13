from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Any, Dict, Optional

from .agent import EarthquakeAgent

app = FastAPI(
    title="Earthquake Monitoring Agent",
    description="Real-time global earthquake monitoring agent for Telex.im",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = EarthquakeAgent()


def extract_text_from_request(data: Dict[str, Any]) -> Optional[str]:
    """Extract text from A2A payload"""
    # Simple keys
    for key in ("text", "message", "prompt", "input", "query"):
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()

    # JSON-RPC format (Telex)
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


@app.get("/")
async def root():
    return {
        "name": "Earthquake Monitoring Agent",
        "version": "1.0.0",
        "status": "active"
    }


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.post("/a2a/agent/earthquake")
async def telex_handler(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    print(f"[A2A] Received body: {body}", flush=True)
    
    text = extract_text_from_request(body)
    if not text:
        text = "recent"
    
    print(f"[A2A] Extracted text: {text}", flush=True)

    result = await agent.process_message(text)

    response = {
        "response": result.response,
        "conversationId": body.get("conversationId"),
        "metadata": {
            "count": len(result.events or []),
            "agent_type": "earthquake_monitor"
        }
    }
    
    print(f"[A2A] Sending response: {response['response'][:100]}...", flush=True)
    return response


@app.on_event("shutdown")
async def shutdown_event():
    await agent.close()