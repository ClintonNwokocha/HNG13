from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
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
class A2ARequest(BaseModel):
    """A2A Protocol request format"""
    prompt: str
    conversationId: Optional[str] = None
    userId: Optional[str] = None
    context: Optional[dict] = None

class A2AResponse(BaseModel):
    """A2A Protocol response format"""
    response: str
    conversationId: Optional[str] = None
    metadata: Optional[dict] = None

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Earthquake Monitoring Agent",
        "version": "1.0.0",
        "status": "active",
        "description": "Real-time global earthquake monitoring"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/a2a/agent/earthquake", response_model=A2AResponse)
async def earthquake_agent_endpoint(request: A2ARequest):
    """
    Main A2A endpoint for telex.im integration

    This endpoint follows the Agent-to-Agent (A2A) protocol
    that telex.im uses to communicate with agents.
    """
    try:
        print(f"[A2A] Received: {request.prompt}")
        
        # Process the message using our agent - USE request.prompt NOT request.message!
        response = await agent.process_message(request.prompt)
        
        print(f"[A2A] Generated response with {len(response.events or [])} events")

        # Format response according to A2A protocol
        return A2AResponse(
            response=response.response,
            conversationId=request.conversationId,
            metadata={
                "events_count": len(response.events) if response.events else 0,
                "agent_type": "earthquake_monitor",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        print(f"[A2A] Error: {str(e)}")
        return A2AResponse(
            response=f"I encountered an error processing your request: {str(e)}",
            conversationId=request.conversationId,
            metadata={"error": True, "error_type": type(e).__name__}
        )
    
@app.post("/chat", response_model=TelexResponse)
async def chat_endpoint(message: TelexMessage):
    """
    Alternative chat endpoint for direct testing
    """
    try:
        response = await agent.process_message(message.message)
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await agent.close()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)