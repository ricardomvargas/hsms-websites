# Backend — HSM Sponsors Website Search

Python + FastAPI + Uvicorn

## First-time setup

These steps are only needed once, when you first clone the project.

### 1. Create a virtual environment

```bash
python3 -m venv .venv
```

### 2. Activate the virtual environment

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Running the server

### Activate the environment (if not already active)

```bash
source .venv/bin/activate
```

### Start the server

```bash
uvicorn app.main:app --reload
```

The server starts at `http://localhost:8000`. The `--reload` flag automatically restarts the server whenever you make changes to the code.

To stop the server, press `Control + C` in the terminal.

## Using the API

### Import companies from IND

```bash
curl -X POST http://localhost:8000/import
```

This fetches the latest sponsor list from the IND website and performs a smart sync (inserts new, updates names, removes gone).

### List all companies

```bash
curl http://localhost:8000/companies
```

### Search companies by name

```bash
curl "http://localhost:8000/companies/search?q=Meeting"
```

### Health check

```bash
curl http://localhost:8000/health
```

## Endpoints

| Method | Path                         | Description                                                                   |
| ------ | ---------------------------- | ----------------------------------------------------------------------------- |
| GET    | `/health`                    | Health check                                                                  |
| POST   | `/import`                    | Sync sponsors from the IND website (inserts new, updates names, removes gone) |
| GET    | `/companies`                 | List companies (paginated, default 20 per page)                               |
| GET    | `/companies/search`          | Search companies by name (paginated, LIKE-based)                              |
| GET    | `/companies/{id}`            | Get a single company                                                          |
| GET    | `/companies/without-website` | List companies missing a website URL                                          |
| PUT    | `/companies/{id}/website`    | Set or update a company's website URL                                         |
| POST   | `/companies/fetch-websites`  | Look up websites for selected companies via DNS + Wikipedia hybrid search     |

### Pagination

`GET /companies` and `GET /companies/search` accept `?page=1&per_page=20` query parameters (max 100 per page).

Response shape:

```json
{
  "items": [...],
  "total": 12881,
  "page": 1,
  "per_page": 20
}
```

### Search

`GET /companies/search?q=<name>` returns companies whose name contains the query string (case-insensitive LIKE search). Supports the same pagination parameters as `/companies`.

### Import behavior

`POST /import` performs a smart sync instead of a full replace:

- Companies new to the IND list are **inserted**
- Companies whose names changed are **updated**
- Companies no longer in the IND list are **removed**
- `website_url` values are **never overwritten** during sync

### Website lookup

`POST /companies/fetch-websites` accepts a JSON body with a list of company IDs and returns website URLs for each:

```json
{
  "company_ids": [1, 2, 3]
}
```

Lookup strategy:

- First tries **DNS-based candidate generation** (strips common suffixes, tries `.nl`, `.eu`, `.com` variants)
- Falls back to **Wikipedia infobox parsing** for companies not found via DNS
- Detects parked domains using keywords in both English and Dutch
- Prefers `.nl` TLD when multiple candidates resolve
- Parking detection: `"dit domein is te koop"`, `"domeinnaam is te koop"`, etc.

## Project structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app, router includes, lifespan
│   ├── database.py              # DB connection + schema init
│   ├── models.py                # Query functions + sync logic
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── companies.py         # /companies, /health, /search endpoints
│   │   └── import_route.py      # /import endpoint
│   └── services/
│       ├── __init__.py
│       ├── ind_scraper.py       # IND website scraper
│       └── website_lookup.py    # DNS + Wikipedia website discovery
├── requirements.txt
├── .venv/                       # Python virtual environment
└── README.md
```

## API Docs

FastAPI generates interactive documentation automatically:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
