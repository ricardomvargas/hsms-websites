---
description: Stop both backend and frontend dev servers.
---

Stop the backend and frontend development servers.

Run `pkill -f "uvicorn app.main" 2>/dev/null` and `pkill -f "vite.js" 2>/dev/null` to kill both processes.
