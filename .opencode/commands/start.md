---
description: Start both backend and frontend dev servers.
---

Start the backend and frontend development servers. The backend runs on port 8000, the frontend on port 5173.

1. Open two terminal tabs.
2. In the first tab: `cd /Users/ricardovargas/Projects/hsms-websites/backend && .venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
3. In the second tab: `cd /Users/ricardovargas/Projects/hsms-websites/frontend && /Users/ricardovargas/.nvm/versions/node/v24.18.0/bin/node ./node_modules/vite/bin/vite.js`
