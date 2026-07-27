---
description: Stop both backend and frontend dev servers.
---

Stop the backend and frontend development servers.

Run `Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force` and `Get-Process -Name node -ErrorAction SilentlyContinue | Stop-Process -Force` to kill both processes.
