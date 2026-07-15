---
description: Create a new branch from main and push upstream
---

Run the following git commands sequentially:
1. `git fetch --prune`
2. `git checkout main`
3. `git pull`
4. `git checkout -b $ARGUMENTS`
5. `git push -u origin $ARGUMENTS`
