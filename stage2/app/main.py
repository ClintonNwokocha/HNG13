from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

# Import database components
from app.database import engine, Base, get_db
from app.routers import countries
from app import crud, schemas
# Load environment variables
load_dotenv()

# Create FastAPI instance
app = FastAPI(
	title="Country Currency & Exchange API",
	description="RESTful API for country data with real-time exchange rate"
)

# Configure CORS
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"]
)

@app.on_event("startup")
async def startup_event():
	print("\n" + "=" * 50)
	print("Country 💵Currency API Starting Up")
	print("=" * 50)

	# Create database tables
	print("Creating database tables")
	Base.metadata.create_all(bind=engine)
	print("Database tables created")

	# Show documentatiosn URLS
	host = os.getenv("HOST", "0.0.0.0")
	port = os.getenv("PORT", "8000")
	print(f"\n API Documentation:")
	print(f"	Swagger UI:	http://localhost:{port}/docs")
	print(f"	ReDoc:		http://localhost:{port}/redoc")
	print(f"	OpenAPI:	http://localhost:{port}/openapi.json")
	print("=" * 50)

@app.on_event("shutdown")
async def shutdown_event():
	print("\n" + "=" * 50)
	print("Country Currency API Shutting Down")
	print("=" * 50)

@app.get("/", tags=["Health"])
def root():

	return {
		"message": "Country Currency & Exchange API",
		"status": "online",
		"version": "1.0.0",
		"documentation": "/docs",
		"endpoints": {
			"refresh": "POST /countries/refresh",
			"list_countries": "GET /countries",
			"get_country": "GET /countries{name}",
			"status": "GET /status",
			"summary_image": "GET /countries/image/summary"
		}
	}

@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
	try:
		db.execute("SELECT 1")
		return {
			"status": "healthy",
			"database": "connected",
			"timestamp": datetime.utcnow().isoformat() + "Z"
		}
	except Exception as e:
		return {
			"status": "unhealthy",
			"database":"disconnected",
			"error": str(e),
			"timestamp": datetime.utcnow().isoformat() + "Z"
		}

@app.get("/status", response_model=schemas.StatusResponse, tags=["Status"])
def get_status(db: Session = Depends(get_db)):
	"""
	Get API statistics.

	Returns:
		- total_countries: Total number of countries in database
		- last_refreshed_at: Timestamp of last data refresh
	"""
	metadata = crud.get_or_create_metadata(db)

	return {
		"total_countries": metadata.total_countries,
		"last_refreshed_at": metadata.last_refreshed_at
}


app.include_router(
	countries.router,
	prefix="/countries",
	tags=["Countries"]
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
	"""
	custom handler for validation errors (422).
	Returns structured error response in required format
	"""
	errors = {}
	for error in exc.errors():
		field = error["loc"][-1]
		message = error["msg"]
		errors[field] = message

	return JSONResponse(
		status_code=400,
		content={
			"error": "Validation failed",
			"details": errors
		}
	)

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
	"""
	Catch-all exception handler for unexpected errors (500).
	Logs the error and returns generic message.
	"""
	import traceback
	print("\n UNEXPECTED ERROR:")
	traceback.print_exc()
	print()

	# Return error response
	# In prroduction, dont expose internal error details
	return JSONResponse(
		status_code=500,
		content={
			"error": "Internal server error",
			"details": str(exc) if os.getenv("DEBUG", "false").lower() == "true" else None
		}
	)



