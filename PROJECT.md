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

## Improvements
1. Good Practices Missing
Broken error handling in routes. companies.py:62 and companies.py:70 return ({"error": "..."}, 404) — this is a Python tuple, not an HTTP 404. FastAPI will serialize it as a 200 OK with the tuple as the body. You need raise HTTPException(status_code=404, detail="...").
No CORS middleware. The frontend (port 5173) won't be able to reach the backend (port 8000) without CORS headers. The app has no CORSMiddleware configured.
Global socket timeout side effect. website_lookup.py:171 uses socket.setdefaulttimeout(5) which sets a process-wide global — this is not thread-safe and affects all socket operations, not just DNS lookups.
No logging anywhere. Failures in the scraper, website lookup, or database operations are silently swallowed. No way to debug issues in production.
No response models. Routes don't define Pydantic response models, making the API harder to document and validate.
Inconsistent DB path. database.py:3 uses hsm.db, but README.md:46 says companies.db.
No pagination on /companies/without-website. Could return thousands of rows at once.

2. Security Concerns
get_companies_by_ids — dynamic IN clause. models.py:94-96 builds the query with f"SELECT ... WHERE id IN ({placeholders})". While the values are parameterized (not injection-vulnerable), there's no upper bound on the ids list. The router caps it at 20, but the model function itself doesn't — any direct caller could pass thousands of IDs. Additionally, if an ids list is empty, the generated SQL WHERE id IN () is invalid SQL and will crash.
update_website accepts arbitrary URLs. companies.py:67-72 — the website_url field is Optional[str] with no validation. A user could store javascript:alert(1) or any arbitrary string. If this data is later rendered in the frontend without sanitization, it's an XSS vector.
No rate limiting. Anyone can hit /import repeatedly to hammer the IND website, or /companies/fetch-websites to make the server send many outbound HTTP requests (potential SSRF-like abuse for reconnaissance).
No authentication/authorization. All endpoints are open — import, website lookup, company updates. Anyone with network access can trigger expensive operations.
Outbound requests to user-influenced URLs. _check_url in website_lookup.py:212 fetches URLs derived from company names. While names come from the IND register (not directly from user input), the flow is: user triggers /fetch-websites → server generates domains from company names → server makes HTTP requests. An attacker who can influence company names in the DB could potentially probe internal network services.

3. Suggested Improvements
Area                            Recommendation
Error handling                  Replace tuple returns with HTTPException. Add a global exception handler for unexpected errors.
CORS                            Add CORSMiddleware with an explicit allowlist of origins (not * in production).
Input validation                Validate URLs with pydantic.HttpUrl or a regex. Add max_length to search queries. 
                                Guard get_companies_by_ids against empty lists.
Rate limiting                   Add slowapi or similar middleware on /import and /fetch-websites.
Auth                            At minimum, add an API key check for write/expensive endpoints (/import, /fetch-websites, 
                                /companies/{id}/website).
DB management                   Use a context manager (with get_connection() as conn:) so connections are always released, 
                                even on exceptions.
Socket timeout                  Pass timeout to socket.getaddrinfo or use dns.resolver instead of mutating global state.
Config                          Move DB_PATH, timeouts, and other magic values to environment variables or a config file.
Logging                         Add structured logging with Python's logging module — at least for errors and external HTTP calls.
Pagination                      Add pagination to /companies/without-website.

The most critical items to fix first are the broken error handling (returns 200 instead of 404), missing CORS, and the unbounded get_companies_by_ids with empty-list edge case.

4. What we decided to do and what was done:
Area                            Recommendation                                                                                      Status
CORS                            Add CORSMiddleware with an explicit allowlist of origins (not * in production).                     ✅ Done
Error handling                  Replace tuple returns with HTTPException. Add a global exception handler for unexpected errors.     ✅ Done
Input validation                Validate URLs with pydantic.HttpUrl or a regex. Add max_length to search queries. 
                                Guard get_companies_by_ids against empty lists.                                                     ✅ Done
Rate limiting                   Add slowapi or similar middleware on /import and /fetch-websites.                                   ✅ Done (only /import)
DB management                   Use a context manager (with get_connection() as conn:) so connections are always released, 
                                even on exceptions.                                                                                 ✅ Done
Socket timeout                  Pass timeout to socket.getaddrinfo or use dns.resolver instead of mutating global state.            ✅ Done
Config                          Move DB_PATH, timeouts, and other magic values to environment variables or a config file.           ✅ Done
Logging                         Add structured logging with Python's logging module — at least for errors and external HTTP calls.
Pagination                      Add pagination to /companies/without-website.