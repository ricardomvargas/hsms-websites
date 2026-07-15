# HSM Sponsors Website Search

## Goal
A web application that helps users find website URLs for companies that are recognized sponsors of the Dutch Highly Skilled Migrant visa program.

## Data Source
The official list of recognized sponsors published by the Dutch Immigration and Naturalisation Service (IND):  
https://ind.nl/en/public-register-recognised-sponsors/public-register-work

## Scope
- Import the IND sponsor list into a local database
- Browse and filter sponsors to find specific companies
- Select one or more organizations
- Discover website URLs via DNS resolution and Wikipedia infobox lookup
- Track discovered website URLs per company

## Features

### Company Management
- Import sponsor list from the IND public register
- Smart sync (insert new, update names, remove gone)
- Store companies in SQLite
- Display companies in the UI for selection

### Filtering
- Text-based company name filter with LIKE search
- Filter button and clear (X) button
- Paginated filter results

### Website Discovery
- DNS-based candidate generation (strips common suffixes, tries `.nl`, `.eu`, `.com` variants)
- Wikipedia infobox fallback for companies not found via DNS
- Parked domain detection (keywords in English and Dutch, marketplace URL checks, JS redirect following)
- `.nl` TLD preference when multiple candidates resolve

## Linting & Formatting
- **Frontend:** oxlint + Prettier
- **Backend:** Ruff (linter + formatter in one)

## Architecture

| Layer | Responsibility |
|-------|---------------|
| **Frontend** (React) | Display data, collect user input, call backend APIs |
| **Backend** (Python) | Import data, execute website lookups, expose REST APIs |
| **Database** (SQLite) | Store companies and their website URLs |

### Website Lookup Approach
- Pure Python (`requests` + `BeautifulSoup`)
- DNS resolution via `socket` module
- No AI/LLM API dependency

## Personal Goals
- Build a tool I can personally use to find company websites for HSM sponsors
- Learn Python through practical, real-world development
- Publish as a public GitHub project for others to use

## Tech Stack
- **Frontend:** React + TypeScript + Vite + pnpm
- **Backend:** Python + FastAPI + Uvicorn
- **Database:** SQLite (via Python `sqlite3` module)
