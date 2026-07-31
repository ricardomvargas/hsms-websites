# AGENTS.md — Project Context for AI Assistants

## Project Overview
A web app that helps users find website URLs for Dutch Highly Skilled Migrant visa program recognized sponsors. Uses the IND public register as the primary source of company data.

## Tech Stack
- **Frontend:** React + TypeScript + Vite + pnpm
- **Backend:** Python + FastAPI
- **Database:** SQLite
- **Data source:** IND Public Register (https://ind.nl/en/public-register-recognised-sponsors/public-register-work)

## Key Conventions
- React with functional components and hooks
- Python backend following PEP 8
- TypeScript preferred for frontend
- Python modules in `backend/` directory
- CSS with BEM methodology (no CSS frameworks or component libraries)
- Simple, clean UI with pure HTML + CSS

## Backend Conventions
- **Config:** all tunables live in `app/config.py` as a `settings` singleton (pydantic-settings). Import it (`from app.config import settings`) — never hardcode paths/timeouts/limits. Values can be overridden via env vars or a `backend/.env` file (see `.env.example`).
- **Database:** always access the DB through the `get_connection()` context manager (`with get_connection() as conn:`). It commits on success and always closes the connection.
- **Logging:** use a module-level `logger = logging.getLogger(__name__)` and log meaningful events (external HTTP calls, batch results, errors). Do not `print()`.
- **DNS resolution:** use dnspython (`dns.resolver`), not the `socket` module, so timeouts are per-call and don't mutate global state.
- **Pagination:** list endpoints follow the same pattern as `/companies` — `page`/`per_page` query params, response `{items, total, page, per_page}`.

## Component Structure
Components follow this folder convention:
```
src/components/
└── component-name/                # kebab-case folder
    ├── component-name.tsx         # main component file in the root
    ├── index.ts                   # barrel exports
    ├── hooks/
    │   └── use-hook-name.ts       # component-specific hooks
    ├── types/
    │   └── component-types.ts     # component-specific types
    └── styles/
        └── styles.css             # component-specific styles
```
- Each component has its own folder named in **kebab-case**
- The component file sits in the **root** of its folder (also kebab-case)
- A root `index.ts` re-exports hooks and types — other files import through it
- Component-specific hooks go in a `hooks/` subfolder
- Component-specific types go in a `types/` subfolder
- Styles (when added) go in a `styles/` subfolder

## Core Features

### Company Management
- Import and store the list of recognized sponsors from the IND website
- Persist company information in a local SQLite database
- Display the list of available companies in the UI
- Allow users to select one or multiple companies
- Discover and store website URLs via DNS + Wikipedia lookup

### Filtering
- Text-based company name filter with LIKE search
- Filter button and clear (X) button
- Paginated filter results (same 20-per-page as main list)
- Filtering resets checkbox selections

## Linting & Formatting

### Frontend (React + TypeScript)
- **oxlint** (configured in `.oxlintrc.json`) — linting for JS/TS/React
- **Prettier** (`.prettierrc`) — code formatting

### Backend (Python)
- **Ruff** (configured in `pyproject.toml`) — linter + formatter (replaces Flake8, isort, Black)

## Architecture

### Frontend Responsibilities
- Display companies
- Collect user's company selections
- Trigger import and website lookup (via REST API)
- Display results

### Backend Responsibilities
- Import and manage sponsor companies
- Execute website lookups (DNS + Wikipedia)
- Expose REST APIs to the frontend

### Database (SQLite)
- Store companies

### Web Scraping
- Pure Python approach using `requests` + `BeautifulSoup`
- No AI/LLM APIs — self-contained, free, and better for learning

## Project Structure (evolving)
```
/
├── frontend/          # React + TypeScript + Vite (pnpm)
│   ├── src/           # Application source code
│   │   ├── components/
│   │   │   ├── paginator/
│   │   │   │   ├── paginator.tsx
│   │   │   │   ├── index.ts
│   │   │   │   └── styles.css
│   │   │   ├── companies-list/
│   │   │   │   ├── companies-list.tsx
│   │   │   │   ├── index.ts
│   │   │   │   ├── hooks/
│   │   │   │   │   └── use-companies.ts
│   │   │   │   ├── types/
│   │   │   │   │   └── companies-types.ts
│   │   │   │   └── styles/
│   │   │   │       └── styles.css
│   │   │   ├── filter-input/
│   │   │   │   ├── filter-input.tsx
│   │   │   │   ├── index.ts
│   │   │   │   └── styles/
│   │   │   │       └── styles.css
│   │   │   └── loader/
│   │   ├── App.tsx
│   │   └── App.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── backend/           # Python + FastAPI
│   ├── .venv/         # Python virtual environment
│   ├── .env.example   # Template for optional local env overrides
│   ├── app/           # Application source code
│   │   ├── main.py    # FastAPI app, router includes, lifespan
│   │   ├── config.py  # settings singleton (pydantic-settings)
│   │   ├── database.py    # DB connection (context manager) + schema init
│   │   ├── models.py      # Query functions + sync logic
│   │   ├── routers/
│   │   │   ├── companies.py   # /companies, /health, /search endpoints
│   │   │   └── import_route.py # /import endpoint
│   │   └── services/
│   │       ├── ind_scraper.py    # IND website scraper
│   │       └── website_lookup.py # DNS (dnspython) + Wikipedia website discovery
│   └── requirements.txt
├── AGENTS.md          # AI context (this file)
├── PROJECT.md         # Human-readable project doc
├── README.md          # Project overview
├── .prettierrc        # Prettier config
├── pyproject.toml     # Python project config (Ruff, etc.)
└── .gitignore
```

## Workflow Rule
- **Only implement when explicitly told to.** Brainstorm and discuss first. If the user says "let's discuss/brainstorm X", do not write any code — just discuss options, trade-offs, and approaches. Wait for explicit "let's implement" or "go ahead" before touching any file.

## Project Goals
- Tool for finding website URLs of Dutch HSM sponsors
- Learning Python (backend development)
- Public GitHub project — code should be presentable, well-structured, and documented

## Design Principles
- Keep dependencies minimal
- Prioritize static/structured data over real-time scraping where possible
- Company data should be cacheable/refreshable
- Code should be beginner-friendly and well-organized (learning project)


