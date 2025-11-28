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
