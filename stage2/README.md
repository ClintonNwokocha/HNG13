# HNG13 Stage 2 - Country Data API

A FastAPI application that fetches country data from REST Countries API, calculates estimated GDP using exchange rates, and provides filtering, sorting, and visualization capabilities.

## Features

- Fetch and cache country data with exchange rates
- Filter countries by region and currency
- Sort by GDP or population
- Generate summary visualization
- RESTful API with comprehensive error handling

## Tech Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **HTTP Client**: httpx
- **Image Generation**: Pillow

## Setup Instructions

### Prerequisites

- Python 3.12+
- PostgreSQL 16+

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/ClintonNwokocha/HNG13.git
cd HNG13/stage2
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup PostgreSQL**
```bash
# Create database and user
psql -U postgres
CREATE DATABASE country_db;
CREATE USER country_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE country_db TO country_user;
\q
```

5. **Configure environment variables**
Create `.env` file:
```env
DATABASE_URL=postgresql://country_user:your_password@localhost:5432/country_db
COUNTRIES_API_URL=https://restcountries.com/v3.1/all
EXCHANGE_API_URL=https://open.er-api.com/v6/latest/USD
CACHE_DIR=cache
```

6. **Run the application**
```bash
uvicorn app.main:app --reload
```

7. **Access the API**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### POST /countries/refresh
Fetch and cache country data with exchange rates

### GET /countries
Get all countries (supports filtering and sorting)
- Query params: `region`, `currency`, `sort`

### GET /countries/{name}
Get specific country by name

### GET /countries/status
Get refresh metadata

### GET /countries/image/summary
Get summary visualization (PNG)

### DELETE /countries/{name}
Delete a country

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | Required |
| COUNTRIES_API_URL | REST Countries API endpoint | https://restcountries.com/v3.1/all |
| EXCHANGE_API_URL | Exchange rates API endpoint | https://open.er-api.com/v6/latest/USD |
| CACHE_DIR | Directory for cached images | cache |

## Testing
```bash
# Test refresh endpoint
curl -X POST http://localhost:8000/countries/refresh

# Test get all countries
curl http://localhost:8000/countries

# Test filter by region
curl "http://localhost:8000/countries?region=Africa"

# Test get specific country
curl http://localhost:8000/countries/Nigeria
```

## Deployment

Deployed on Railway.app with PostgreSQL database.

## Author

Clinton Nwokocha - HNG13 Backend Track

## License

MIT