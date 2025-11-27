# Deploy to Coolify (Docker)

This guide shows how to deploy the Flask Market Analysis app to Coolify using the Dockerfile in this folder.

## Prerequisites
- A Coolify instance with a connected Git repository containing this project
- Domain (optional but recommended) pointing to Coolify

## Repo layout
- Dockerfile is at: `app/Dockerfile`
- App entry: `app/app.py` (Flask app object: `app`)
- Frontend served at `/` from `market_app.html`
- API available at `/api/*`

## App expectations
- The app listens on port `8080` by default (env `PORT`)
- SQLite database path is configurable via env `DATABASE_PATH` (default `/data/market_data.db`)
- The container exposes port 8080

## Create an Application in Coolify
1. Add a new **Application**
2. Choose your Git repository & branch
3. Build settings:
   - Base Directory: `app`
   - Build Pack / Type: `Dockerfile`
   - Dockerfile Path: `Dockerfile`
4. Network:
   - HTTP Port (internal): `8080`
   - Expose HTTP to the internet: yes
5. Domains:
   - Assign your domain (optional) and enable HTTPS

## Environment variables
Add the following environment variables in the Application > Settings > Environment:
- `PORT=8080` (optional, defaults to 8080)
- `DATABASE_PATH=/data/market_data.db`
- `GUNICORN_WORKERS=2` (optional)

## Persistent storage (SQLite)
Add a **Persistent Storage** mount so your database survives deployments:
- Source: a new volume (e.g. `market_data`)
- Mount Path: `/data`

## Healthcheck
The Dockerfile defines a healthcheck hitting `/api/imports`.
If you prefer Coolify’s own healthcheck, use path `/api/imports` (expect 200).

## Build & deploy
- Click **Deploy**. Coolify will build the Dockerfile from `app/` and run Gunicorn.
- On success, visit your domain (or the generated URL). The frontend loads at `/` and calls the API at `/api`.

## Notes
- The frontend’s `API_BASE` is set to `/api` for same-origin calls in production.
- To scale up workers, increase `GUNICORN_WORKERS`.
- To reset the DB, delete the mounted volume (`/data`) and redeploy.

## Local Docker (optional)
You can test the same image locally:

```bash
# From the repo root
cd app

docker build -t market-app:latest .

docker run --rm -p 8080:8080 \
  -e PORT=8080 \
  -e DATABASE_PATH=/data/market_data.db \
  -v market_data:/data \
  market-app:latest
```

Then open http://localhost:8080
