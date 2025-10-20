from fastapi import FastAPI
from fastapi.responses import JSONResponse
import requests
from datetime import datetime, timezone


app = FastAPI()

@app.get("/me")
def get_profile():
    try:
        # Fetch cat fact
        response = requests.get("https://catfact.ninja/fact", timeout=5)
        response.raise_for_status()
        cat_fact = response.json().get("fact", "cat are mysterious creatures!!!")
    except Exception as e:
        print("Error fetching cat fact:", e)
        cat_fact = "Could not fetch cat fact at the moment."

    # Current UTC time in ISO 8601 format
    timestamp = datetime.now(timezone.utc).isoformat()


    result = {
        "status": "success",
        "user": {
            "email": "leoclinton2011@hotmail.com",
            "name": "Nwokocha Chiedozie Clinton",
            "stack": "Python/FastAPI"
        },
        "timestamp": timestamp,
        "fact": cat_fact
    }


    return JSONResponse(content=result, media_type="application/json")