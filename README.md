# HSM Sponsors Website Search

A web application that helps find website URLs for Dutch Highly Skilled Migrant visa program recognized sponsors using the IND public register.

## Features

- Import and sync the sponsor list from the IND Public Register
- Browse companies with a paginated, searchable list
- Filter companies by name
- Discover website URLs via DNS + Wikipedia hybrid lookup
- Track company website URLs

## Project structure

```
frontend/   React + TypeScript + Vite (pnpm)
backend/    Python + FastAPI + SQLite
```

## Quick start

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API runs at `http://localhost:8000`.

### Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

App runs at `http://localhost:5173`.

## Database

Companies and their website URLs are stored in a local SQLite database at `backend/companies.db`. The database is created automatically on first run.

## Data source

[IND Public Register — Work](https://ind.nl/en/public-register-recognised-sponsors/public-register-work)
