# Quick Start Guide - Market Analysis API

## Installation & Setup

### 1. Install Dependencies
```bash
cd /Users/maysam/Workspace/aralel/aralel-software-studios/app
pip install -r requirements.txt
```

### 2. Start the Flask Server
```bash
cd /Users/maysam/Workspace/aralel/aralel-software-studios/app
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

The SQLite database (`market_data.db`) will be created automatically on first run.

### 3. Open the Frontend
Open `index.html` in your web browser:
```bash
open index.html
```

## Usage

### Upload Data
1. Go to the **Upload Data** tab
2. Drag and drop a JSON file (or click to browse)
3. The file will be analyzed and automatically uploaded to the database
4. The file's creation date will be detected and stored

### View History
1. Click the **History** tab
2. See all previous imports with their dates
3. Click **View** on any import to see its data

### Compare Data
1. Click the **Compare** tab
2. A line chart across all imports loads automatically
3. Use the checkboxes to toggle attributes: Current, Change %, Growth, Appeal
4. Defaults: Current and Change %

## Data Format

Your JSON file should match the format from `market.html`:

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

## Files Created

- **app.py** - Flask API backend
- **index.html** - Frontend with tabs for upload/history/compare
- **requirements.txt** - Python dependencies
- **README_MARKET_API.md** - Full API documentation
- **market_data.db** - SQLite database (auto-created)

## API Endpoints

All endpoints are available at `http://localhost:5000/api/`

- `POST /upload` - Upload new data
- `GET /imports` - List all imports
- `GET /imports/<id>` - Get specific import data
- `POST /compare` - Compare two imports
- `GET /timeseries` - Time series across all imports per stock

See `README_MARKET_API.md` for detailed API documentation.

## Troubleshooting

### Port Already in Use
If port 5000 is busy, edit `app.py` and change:
```python
app.run(debug=True, port=5000)
```
to a different port like 5001.

### CORS Errors
Make sure Flask-CORS is installed:
```bash
pip install Flask-CORS
```

### Database Issues
Delete `market_data.db` to reset the database:
```bash
rm market_data.db
python app.py  # Will recreate the database
```

## Docker (Quick)

### Local test
```bash
cd app
docker build -t market-app:latest .
docker run --rm -p 8080:8080 \
  -e PORT=8080 \
  -e DATABASE_PATH=/data/market_data.db \
  -v market_data:/data \
  market-app:latest
```
Open http://localhost:8080

### Coolify (summary)
- Base Directory: `app`
- Dockerfile Path: `Dockerfile`
- Internal Port: `8080`
- Env: `DATABASE_PATH=/data/market_data.db` (optional `PORT`, `GUNICORN_WORKERS`)
- Persistent Storage: mount `/data`

See `DEPLOYMENT_COOLIFY.md` for step-by-step instructions.
