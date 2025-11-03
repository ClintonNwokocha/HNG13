# 🌍 Earthquake Monitoring Agent for Telex.im

A real-time global earthquake monitoring AI agent that provides detailed seismic event information with customizable alerts based on magnitude, time, and location.

## 🎯 What It Does

This intelligent agent monitors earthquakes worldwide using live data from the USGS (United States Geological Survey) and helps users:

- **Track Real-Time Earthquakes**: Get instant updates on seismic events globally
- **Filter by Criteria**: Search by magnitude, location, time range
- **Natural Language Queries**: Ask questions in plain English
- **Alert Levels**: Includes USGS alert levels (Green, Orange, Red) and tsunami warnings
- **Detailed Information**: Provides coordinates, depth, timestamps, and direct links to official USGS pages

## 🚀 Features

### Smart Query Understanding
The agent understands natural language queries like:
- "Show earthquakes above magnitude 5"
- "Earthquakes in California in the last 24 hours"
- "Any major earthquakes today?"
- "Show me the last 10 earthquakes"
- "Magnitude 6+ events near Japan"

### Rich Data Display
- 📊 Magnitude and precise location
- 📅 Timestamps in UTC
- 📍 Latitude/Longitude coordinates
- 🔽 Depth in kilometers
- ⚠️ USGS alert levels (GREEN/ORANGE/RED)
- 🌊 Tsunami warnings
- 🔗 Direct links to USGS event pages

### Filtering Options
- **Magnitude**: Filter by minimum/maximum earthquake magnitude
- **Time Range**: Last hour, 24 hours, week, or custom hours
- **Location**: Search specific regions (countries, states, cities)
- **Result Limit**: Control number of results returned

## 🛠️ Technology Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **HTTP Client**: httpx (async)
- **Data Validation**: Pydantic
- **Data Source**: USGS Earthquake API
- **Protocol**: A2A (Agent-to-Agent) for Telex.im

## 📋 Requirements

- Python 3.11 or higher
- pip package manager
- Active internet connection (for USGS API)

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ClintonNwokocha/HNG13.git
cd HNG13/stage3
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at `http://localhost:8000`

## 📡 API Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy"
}
```

### Root Endpoint
```http
GET /
```

**Response:**
```json
{
  "name": "Earthquake Monitoring Agent",
  "version": "1.0.0",
  "status": "active",
  "description": "Real-time global earthquake monitoring with customizable alerts"
}
```

### A2A Endpoint (Telex.im Integration)
```http
POST /a2a/agent/earthquake
Content-Type: application/json
```

**Request Body:**
```json
{
  "prompt": "Show earthquakes above magnitude 5",
  "context": {},
  "user_id": "optional-user-id"
}
```

**Response:**
```json
{
  "text": "🌍 Found 8 earthquake(s) in the last 24 hours:\n\n1. Magnitude 6.3 - 22 km WSW of Khulm, Afghanistan...",
  "metadata": {
    "events_count": 8,
    "agent_type": "earthquake_monitor",
    "timestamp": "2025-11-03T12:00:00"
  }
}
```

### Chat Endpoint (Testing)
```http
POST /chat
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "Show earthquakes in Japan",
  "user_id": "optional",
  "channel_id": "optional"
}
```

**Response:**
```json
{
  "response": "🌍 Found 3 earthquake(s)...",
  "events": [
    {
      "id": "us6000rl31",
      "magnitude": 5.8,
      "place": "22 km E of Tokyo, Japan",
      "time": "2025-11-03T10:30:00",
      "latitude": 35.68,
      "longitude": 139.77,
      "depth": 45.2,
      "url": "https://earthquake.usgs.gov/earthquakes/eventpage/us6000rl31",
      "alert_level": "green",
      "tsunami": false
    }
  ]
}
```

## 🧪 Testing

### Using FastAPI Interactive Docs

1. Start the server: `uvicorn app.main:app --reload`
2. Open browser: `http://localhost:8000/docs`
3. Click on any endpoint
4. Click "Try it out"
5. Enter test data and click "Execute"

### Using cURL

**Test Health:**
```bash
curl http://localhost:8000/health
```

**Test Earthquake Query:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show earthquakes above magnitude 5"
  }'
```

**Test A2A Endpoint:**
```bash
curl -X POST "http://localhost:8000/a2a/agent/earthquake" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Earthquakes in California today"
  }'
```

## 🌐 Deployment

### Deploy on Railway.app

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Deploy
cd stage3
railway init
railway up
```

## 🔗 Telex.im Integration

### 1. Get Telex Access

In your Telex workspace, run:
```
/telex-invite your-email@example.com
```

### 2. Create Workflow JSON

Save as `telex_workflow.json`:

```json
{
  "active": true,
  "category": "monitoring",
  "description": "Real-time global earthquake monitoring agent",
  "id": "earthquake_monitor_v1",
  "long_description": "\nYou are an intelligent earthquake monitoring assistant that provides real-time information about seismic events worldwide.\n\nYour primary functions:\n- Monitor earthquakes globally using USGS data\n- Filter events by magnitude, time range, and location\n- Provide detailed event information including coordinates, depth, and alerts\n- Alert users to significant seismic activity and tsunami warnings\n\nWhen responding:\n- Always provide clear, formatted earthquake data\n- Include relevant details: magnitude, location, time, coordinates, depth\n- Highlight any tsunami warnings or alert levels\n- Be concise but informative\n- Help users understand the significance of earthquake magnitudes\n- If location is ambiguous, ask for clarification\n- Default to magnitude 4.5+ for the last 24 hours if no criteria specified\n",
  "name": "earthquake_monitor",
  "nodes": [
    {
      "id": "earthquake_agent",
      "name": "Earthquake Monitoring Agent",
      "parameters": {},
      "position": [500, 200],
      "type": "a2a/mastra-a2a-node",
      "typeVersion": 1,
      "url": "https://your-deployed-url.onrender.com/a2a/agent/earthquake"
    }
  ],
  "pinData": {},
  "settings": {
    "executionOrder": "v1"
  },
  "short_description": "Monitor earthquakes worldwide with customizable alerts"
}
```

**Important**: Replace `your-deployed-url` with your actual Render URL!

### 3. Upload to Telex

- Go to Telex.im
- Navigate to workflows/agents section
- Upload your `telex_workflow.json`
- Test your agent!

### 4. View Logs

Check agent interactions at:
```
https://api.telex.im/agent-logs/{channel-id}.txt
```

Get channel-id from your Telex URL.

## 💡 Example Queries

The agent understands various query formats:

| Query | What It Does |
|-------|--------------|
| `"hello"` | Shows welcome message and usage examples |
| `"help"` | Displays detailed help and filtering options |
| `"Show earthquakes above magnitude 5"` | Lists all 5.0+ magnitude earthquakes in last 24h |
| `"Earthquakes in California today"` | Filters by location and time |
| `"Show 10 recent earthquakes"` | Limits results to 10 most recent |
| `"Magnitude 6+ in Japan last week"` | Combines magnitude, location, and time filters |
| `"Earthquakes in the last 12 hours"` | Custom time range |

## 🏗️ Project Structure

```
stage3/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI application & endpoints
│   ├── models.py            # Pydantic data models
│   ├── earthquake.py        # USGS API client
│   └── agent.py             # Agent logic & NLP parsing
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🧠 How It Works

### 1. Query Processing
```
User Query → Agent parses with regex → Extracts filters (magnitude, location, time)
```

### 2. Data Fetching
```
Filters → USGS API request → JSON response → Parse & filter results
```

### 3. Response Formatting
```
Raw data → Format with emojis & structure → Return to user
```

### 4. Architecture Flow
```
Telex.im → A2A Protocol → FastAPI Agent → USGS API → Response
```

## 📊 Data Source

All earthquake data comes from the **USGS Earthquake Hazards Program**:
- API: https://earthquake.usgs.gov/fdsnws/event/1/
- Real-time data updated every few minutes
- Global coverage
- Authoritative source for seismic information

## 🎨 Understanding Alert Levels

- **GREEN**: Minimal impact expected
- **ORANGE**: Significant damage possible in vulnerable structures
- **RED**: Widespread damage likely

## 🐛 Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Use different port
uvicorn app.main:app --port 8001
```

### No earthquakes found
- Try lower magnitude threshold (e.g., 4.0)
- Check USGS API status: https://earthquake.usgs.gov/
- Verify internet connection

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 🤝 Contributing

This project was built for HNG Internship Stage 3. Suggestions and improvements are welcome!

## 📝 License

MIT License - feel free to use for learning and projects

## 👨‍💻 Author

**Clinton Nwokocha**
- GitHub: [@ClintonNwokocha](https://github.com/ClintonNwokocha)
- Project: HNG Internship Stage 3 Backend Challenge

## 🙏 Acknowledgments

- **USGS** for providing free, real-time earthquake data
- **Telex.im** for the A2A protocol and platform
- **HNG Internship** for the learning opportunity and challenge
- **FastAPI** for the excellent web framework

## 📚 Resources

- [USGS Earthquake API Documentation](https://earthquake.usgs.gov/fdsnws/event/1/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Telex.im Documentation](https://telex.im)
- [HNG Internship](https://hng.tech)

---


*Last Updated: November 3, 2025*