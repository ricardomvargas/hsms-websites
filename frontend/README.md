# Frontend — HSM Sponsors Website Search

React + TypeScript + Vite + pnpm

## Setup

```bash
pnpm install
```

## Development

```bash
pnpm dev
```

Starts dev server at `http://localhost:5173`. Proxies `/companies`, `/import`, `/health` to the backend at `http://localhost:8000`.

## Build

```bash
pnpm build
```

## Lint

```bash
pnpm lint
```

## Features

### App Layout
- Single-column layout with centered title
- Section header: filter input on the left, action buttons on the right
- Full-width company table with scroll
- Paginator fixed at the bottom of the screen

### Company list
- Paginated list of all IND sponsor companies (20 per page)
- Each row shows: company name, website URL (or "No website"), and KvK number
- Column headers: Company (40%), Website (40%), KvK (20%)
- Checkboxes for selecting individual companies or all on the current page
- Selections clear when navigating to a different page

### Filter
- Text input with Filter button and X clear button
- Company name search via backend LIKE query
- Filter results are paginated
- Clear (X) button is disabled when no filter is active
- Filtering resets checkbox selections
- "Filtering..." loader shown while filtering

### Paginator
- Shows: Previous, up to 10 page numbers, Next
- Previous/Next jump between sections of 10 pages
- Current page is highlighted
- Paginator hidden when all results fit on one page

### Import
- "Import from IND" button triggers a smart sync
- New companies are added, removed companies are deleted, existing website URLs are preserved
- Import clears any active filter and resets to page 1

### Website Lookup
- "Get website info" button (enabled when companies are selected)
- Triggers DNS + Wikipedia hybrid lookup via the backend
- Results refresh after lookup completes, preserving any active filter
- "Loading..." overlay shown during the process
