---
description: Start both backend and frontend dev servers.
---

Start the backend and frontend development servers. The backend runs on port 8000, the frontend on port 5173.

1. Open two terminal tabs.
2. In the first tab: `cd backend && .venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
3. In the second tab: `cd frontend && pnpm dev`
