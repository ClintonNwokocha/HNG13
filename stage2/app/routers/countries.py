"""
Country API endpoints.
All routes related to country data management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import os
from pathlib import Path

from app.database import get_db
from app import crud, schemas
from app.external_apis import fetch_countries, fetch_exchange_rates
from app.image_generator import generate_summary_image

router = APIRouter()


@router.post("/refresh", response_model=schemas.RefreshResponse)
async def refresh_countries(db: Session = Depends(get_db)):
    """
    Fetch all countries and exchange rates, then cache them in database.
    
    **Process:**
    1. Fetch countries from restcountries.com
    2. Fetch exchange rates from open.er-api.com
    3. Match currencies with rates
    4. Calculate estimated GDP
    5. Store or update in database
    6. Generate summary image
    
    **Returns:**
    - Statistics about the refresh operation
    
    **Errors:**
    - 503: External API unavailable
    """
    try:
        # Fetch data from external APIs
        print("📡 Fetching countries from external API...")
        countries_data = await fetch_countries()
        
        print("💱 Fetching exchange rates...")
        exchange_rates = await fetch_exchange_rates()
        
        print(f"✅ Fetched {len(countries_data)} countries and {len(exchange_rates)} exchange rates")
        
        # Process each country
        created_count = 0
        updated_count = 0
        
        for country_data in countries_data:
            country, was_created = crud.create_or_update_country(
                db=db,
                country_data=country_data,
                exchange_rates=exchange_rates
            )
            
            if country is None:
                continue
            if was_created:
                created_count += 1
            else:
                updated_count += 1
        
        # Update metadata
        total_countries = db.query(crud.models.Country).count()
        crud.update_metadata(db, total_countries)
        
        # Get top countries for image
        top_countries = crud.get_top_countries_by_gdp(db, limit=5)
        
        # Generate summary image
        cache_dir = os.getenv("CACHE_DIR", "cache")
        image_path = os.path.join(cache_dir, "summary.png")
        
        try:
            generate_summary_image(
                total_countries=total_countries,
                top_countries=top_countries,
                last_refresh=datetime.utcnow(),
                output_path=image_path
            )
            print(f"🖼️ Summary image generated at {image_path}")
        except Exception as img_error:
            print(f"⚠️ Warning: Could not generate image: {str(img_error)}")
        
        return {
            "message": "Countries refreshed successfully",
            "countries_processed": len(countries_data),
            "countries_created": created_count,
            "countries_updated": updated_count,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        error_message = str(e)
        
        # Determine which API failed
        if "countries" in error_message.lower():
            api_name = "restcountries.com"
        elif "exchange" in error_message.lower():
            api_name = "open.er-api.com"
        else:
            api_name = "external API"
        
        raise HTTPException(
            status_code=503,
            detail={
                "error": "External data source unavailable",
                "details": f"Could not fetch data from {api_name}: {error_message}"
            }
        )


@router.get("", response_model=List[schemas.CountryResponse])
def get_countries(
    region: Optional[str] = Query(None, description="Filter by region (e.g., Africa)"),
    currency: Optional[str] = Query(None, description="Filter by currency code (e.g., NGN)"),
    sort: Optional[str] = Query(None, description="Sort order: gdp_desc, gdp_asc, population_desc, population_asc"),
    db: Session = Depends(get_db)
):
    """
    Get all countries from database with optional filtering and sorting.
    
    **Query Parameters:**
    - **region**: Filter by region (e.g., ?region=Africa)
    - **currency**: Filter by currency code (e.g., ?currency=NGN)
    - **sort**: Sort order - gdp_desc, gdp_asc, population_desc, population_asc
    
    **Examples:**
    - GET /countries
    - GET /countries?region=Africa
    - GET /countries?currency=NGN
    - GET /countries?region=Africa&sort=gdp_desc
    
    **Returns:**
    - List of country objects
    """
    countries = crud.get_all_countries(
        db=db,
        region=region,
        currency=currency,
        sort=sort
    )
    return countries

@router.get("/status", response_model=schemas.StatusResponse)
def get_status(db: Session = Depends(get_db)):
    metadata = crud.get_or_create_metadata(db)
    
    return {
        "total_countries": metadata.total_countries,
        "last_refreshed_at": metadata.last_refreshed_at
    }

@router.get("/image/summary")
def get_summary_image():
    """
    Serve the generated summary image.
    
    **Returns:**
    - PNG image file
    
    **Errors:**
    - 404: Image not found (run POST /countries/refresh first)
    """

    
    cache_dir = os.getenv("CACHE_DIR", "cache")
    image_path = os.path.join(cache_dir, "summary.png")
    
    # Debug information
    print(f"🔍 Current working directory: {os.getcwd()}")
    print(f"🔍 Cache dir: {cache_dir}")
    print(f"🔍 Image path: {image_path}")
    print(f"🔍 Absolute path: {os.path.abspath(image_path)}")
    print(f"🔍 File exists: {os.path.exists(image_path)}")
    
    # List files in cache directory
    if os.path.exists(cache_dir):
        print(f"🔍 Files in cache dir: {os.listdir(cache_dir)}")
    else:
        print(f"🔍 Cache directory doesn't exist!")
    
    if not os.path.exists(image_path):
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Summary image not found. Please run POST /countries/refresh first.",
                "debug": {
                    "looking_for": os.path.abspath(image_path),
                    "cache_dir_exists": os.path.exists(cache_dir),
                    "files_in_cache": os.listdir(cache_dir) if os.path.exists(cache_dir) else []
                }
            }
        )
    
    return FileResponse(image_path, media_type="image/png")



@router.get("/{name}", response_model=schemas.CountryResponse)
def get_country(name: str, db: Session = Depends(get_db)):
    """
    Get a single country by name.
    
    **Path Parameters:**
    - **name**: Country name (case-insensitive)
    
    **Examples:**
    - GET /countries/Nigeria
    - GET /countries/ghana
    
    **Returns:**
    - Country object
    
    **Errors:**
    - 404: Country not found
    """
    country = crud.get_country_by_name(db, name)
    
    if not country:
        raise HTTPException(
            status_code=404,
            detail={"error": "Country not found"}
        )
    
    return country


@router.delete("/{name}")
def delete_country(name: str, db: Session = Depends(get_db)):
    """
    Delete a country by name.
    
    **Path Parameters:**
    - **name**: Country name (case-insensitive)
    
    **Returns:**
    - Success message
    
    **Errors:**
    - 404: Country not found
    """
    deleted = crud.delete_country(db, name)
    
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail={"error": "Country not found"}
        )
    
    # Update metadata
    total_countries = db.query(crud.models.Country).count()
    crud.update_metadata(db, total_countries)
    
    return {
        "message": f"Country '{name}' deleted successfully",
        "deleted": True
    }