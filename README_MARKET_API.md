# Market Analysis API

A Flask-based API for storing and analyzing market data over time with SQLite database backend.

## Features

- **Upload Market Data**: Store JSON market data with timestamps
- **Historical Tracking**: View all past imports with metadata
- **Time Series Comparison**: Compare market data across all imports with interactive line charts (Current, Change %, Growth, Appeal)
- **Automatic Date Detection**: Frontend detects file creation date and sends it to backend
- **RESTful API**: Clean API endpoints for all operations

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Flask Server

```bash
python app.py
```

The server will start on `http://localhost:5000` and automatically create the SQLite database on first run.

### 3. Open the Frontend

Open `market_app.html` in your web browser. The frontend will connect to the Flask API automatically.

## API Endpoints

### Upload Data
**POST** `/api/upload`

Upload market data with a timestamp.

**Request Body:**
```json
{
  "file_date": "2024-01-15T10:30:00Z",
  "data": [
    {
      "name": "AAPL",
      "current": 150.0,
      "target": 180.0,
      "buy": 75,
      "hold": 20,
      "sell": 5,
      "trend": "positive",
      ...
    }
  ]
}
```

### Get Time Series
**GET** `/api/timeseries`

Returns the time series across all imports for each stock, ordered by date.

**Response:**
```json
{
  "dates": ["2025-11-20 10:00:00", "2025-11-21 10:00:00", "2025-11-22 10:00:00"],
  "series": [
    {
      "name": "AAPL",
      "points": [
        { "date": "2025-11-20 10:00:00", "current": 150.0, "target": 180.0, "growth": 120.0, "appeal": 85.5, "change": null },
        { "date": "2025-11-21 10:00:00", "current": 155.0, "target": 182.0, "growth": 117.4, "appeal": 86.0, "change": 3.33 },
        { "date": "2025-11-22 10:00:00", "current": 153.0, "target": 181.0, "growth": 118.3, "appeal": 84.9, "change": -1.29 }
      ]
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "import_id": 1,
  "records_count": 50,
  "file_date": "2024-01-15T10:30:00Z"
}
```

### Get All Imports
**GET** `/api/imports`

Retrieve a list of all imports with metadata.

**Response:**
```json
[
  {
    "id": 1,
    "file_date": "2024-01-15T10:30:00Z",
    "import_date": "2024-01-15T10:35:00Z",
    "metadata": {"count": 50},
    "record_count": 50
  }
]
```

### Get Import Data
**GET** `/api/imports/<import_id>`

Get all market records for a specific import.

**Response:**
```json
{
  "import_info": {
    "id": 1,
    "file_date": "2024-01-15T10:30:00Z",
    "import_date": "2024-01-15T10:35:00Z",
    "metadata": {"count": 50}
  },
  "records": [
    {
      "id": 1,
      "name": "AAPL",
      "current": 150.0,
      "target": 180.0,
      "growth": 120.0,
      "appeal": 85.5,
      ...
    }
  ]
}
```

### Compare Imports
**POST** `/api/compare`

Compare market data between two imports.

**Request Body:**
```json
{
  "import_id1": 1,
  "import_id2": 2
}
```

**Response:**
```json
{
  "import_id1": 1,
  "import_id2": 2,
  "comparison": [
    {
      "name": "AAPL",
      "in_both": true,
      "current_1": 150.0,
      "current_2": 155.0,
      "current_change": 3.33,
      "growth_1": 120.0,
      "growth_2": 122.0,
      ...
    }
  ]
}
```

## Database Schema

### imports table
- `id`: Primary key
- `file_date`: Timestamp from the original file
- `import_date`: Timestamp when data was imported
- `metadata`: JSON metadata about the import

### market_records table
- `id`: Primary key
- `import_id`: Foreign key to imports table
- `name`: Stock/asset name
- `current`: Current price
- `target`: Target price
- `growth`: Calculated growth percentage
- `appeal`: Calculated appeal score
- `buy`, `hold`, `sell`: Analyst ratings
- `relative_change`, `absolute_change`, `daily_change`: Price changes
- `cap`: Market cap
- `trend`: Trend direction
- `raw_data`: Original JSON data

## Usage

### Frontend Features

1. **Upload Tab**: Drag and drop JSON files or click to select
2. **History Tab**: View all past imports and click to view details
3. **Compare Tab**: Interactive line chart across all imports with attribute toggles
   - Toggle attributes: Current, Change %, Growth, Appeal
   - Defaults: Current and Change %

### Data Format

The expected JSON format matches the original market.html structure:

```json
[
  {
    "name": "Apple Inc.",
    "current": "150.25 $",
    "target": "180.00 $",
    "buy": "75%",
    "hold": "20%",
    "sell": "5%",
    "relative": "2.5%",
    "absolute": "3.75 $",
    "daily_change": "1.2%",
    "cap": "2.5T",
    "trend": "trTrendArrow -xsmall -positive trPerformanceMeter__arrow"
  }
]
```

## Notes

- The database file `market_data.db` will be created automatically
- File dates are detected from the file's `lastModified` timestamp in the browser
- All timestamps are stored in UTC
- The comparison feature shows percentage changes and highlights additions/removals

## Files

- `app.py`: Flask API backend
- `market_app.html`: Frontend with database integration
- `market.html`: Original standalone version
- `requirements.txt`: Python dependencies
- `market_data.db`: SQLite database (created automatically)

## Docker

### Local (optional)

```bash
cd app
docker build -t market-app:latest .
docker run --rm -p 8080:8080 \
  -e PORT=8080 \
  -e DATABASE_PATH=/data/market_data.db \
  -v market_data:/data \
  market-app:latest
```

Open http://localhost:8080. The frontend is served at `/` and the API at `/api`.

### Coolify

Use the Dockerfile in `app/` to deploy on Coolify. Key settings:

- Base Directory: `app`
- Dockerfile Path: `Dockerfile`
- Internal Port: `8080`
- Env: `DATABASE_PATH=/data/market_data.db`, optionally `PORT=8080`, `GUNICORN_WORKERS=2`
- Persistent Storage: mount a volume to `/data`

See `DEPLOYMENT_COOLIFY.md` for step-by-step instructions.
