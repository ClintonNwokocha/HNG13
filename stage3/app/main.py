from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any, Dict
import uvicorn
from .agent import EarthquakeAgent
from .models import TelexMessage, TelexResponse


app = FastAPI(
    title="Earthquake Monitoring Agent",
    description="Real-time global earthquake monitoring agent for Telex.im",
    version="1.0.0"
)

# Add CORS middleware for Telex.im integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent
agent = EarthquakeAgent()

# Telex.im A2A Protocol Models
class A2AResponse(BaseModel):
    """A2A Protocol response format"""
    response: str
    conversationId: Optional[str] = None
    metadata: Optional[dict] = None

def extract_text_from_request(data: Dict[str, Any]) -> Optional[str]:
    """Extract user text from various request formats including JSON-RPC"""
    
    # Try direct text fields first
    for key in ['prompt', 'message', 'text', 'input', 'query']:
        if key in data and isinstance(data[key], str):
            return data[key]
    
    # Handle JSON-RPC format from Telex
    if 'params' in data:
        params = data['params']
        if isinstance(params, dict) and 'message' in params:
            msg = params['message']
            if isinstance(msg, dict) and 'parts' in msg:
                # Extract text from parts array
                parts = msg['parts']
                if isinstance(parts, list):
                    for part in parts:
                        if isinstance(part, dict) and part.get('kind') == 'text':
                            text = part.get('text', '').strip()
                            if text:
                                return text
    
    return None