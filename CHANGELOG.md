# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

- Database indexing improvements for SQLite schema in `app.py`:
  - Verified existing indexes: `imports(file_date)`, `market_records(name, import_id)`.
  - Ensured additional indexes exist to optimize join and sort patterns:
    - `market_records(import_id)` to accelerate joins and lookups by import.
    - `market_records(import_id, appeal DESC)` to optimize `ORDER BY appeal DESC` with `WHERE import_id = ?`.
- Index creation is idempotent and occurs in `init_db()` on app startup; no manual migration required.
- No changes to environment variables or external services.

- Feature: Stock history view and API
  - Added `GET /api/stock_history?name=...` to return historical records for a stock ordered by date.
  - Added `stock_history.html` page and `/stock_history.html` route to display the history in a table.
  - Made stock names clickable in tables; clicking opens the stock history page in a new tab.
  - Added a Chart tab in `stock_history.html` with ECharts line charts and selectable metrics (current, target, growth, appeal, buy/hold/sell, relative, daily).
  - Chart tab controls now show colored dots and labels matching series colors (acts as a legend).
  - UI: Long stock names now wrap in tables and compare labels to avoid overflow.
  - Feature: Stock history table columns are sortable via clickable headers (date, numeric metrics, cap with T/B/M/K parsing, trend as text).
  - Feature: History tab's import table is now sortable by clicking column headers; clicking View auto-scrolls to the rendered table.
  - Rename: Main frontend entry is now `index.html`; Flask `/` serves `index.html`. Legacy `/market_app.html` remains for compatibility. Back links updated accordingly.

- Fix: Chart toggles in stock history
  - Unchecking attributes now removes the corresponding series reliably by clearing the chart and applying options with `notMerge=true`.

- Fix: Flask 3 compatibility
  - Removed deprecated `before_first_request` usage; DB initialization now happens in `__main__` during local runs.

- CI: GitHub Actions
  - Added `.github/workflows/python-app.yml` to install dependencies, import-check `app.py`, byte-compile sources, and run a basic Flask route smoke test on every push/PR.
