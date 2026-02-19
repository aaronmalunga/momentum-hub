**Demo Mode & Reviewer Guide**

- **Purpose:** Demo mode lets reviewers or new users explore Momentum with pre-populated example habits without touching a user's real data in `momentum.db`.

- **Demo DB (isolated):** By default, local demo runs write to `momentum_demo.db`. The main app (`momentum_main.py`) defaults to `momentum.db` and will not use demo data unless instructed.
- **Primary DB creation:** The primary database file (`momentum.db`) is created locally on first run and is not included in the repository, so new users start with an empty database unless they explicitly use demo mode or seed data.

- **Quick commands for reviewers:**
  - Seed the demo DB (safe default):
    - ``python scripts/seed_demo_db.py --overwrite``
  - Launch the CLI in demo mode (auto-seeds demo habits and uses `momentum_demo.db`):
    - ``python momentum_main.py --demo``
  - Launch the CLI explicitly using the demo DB:
    - ``python momentum_main.py --db momentum_demo.db``

- **Demo using the primary DB (not recommended):**
  - Use the seeder with an explicit target and overwrite (this may replace the current `momentum.db`):
  - ``python scripts/seed_demo_db.py --db momentum.db --overwrite``
  - Warning: the seeder attempts a backup when possible - run only when intentionally replacing the primary DB.

- **CI behavior:** The seeder used in CI defaults to `momentum.db` so automated tests find seeded data. This does not affect local environments.

- **Notes for maintainers / reviewers:**
  - `--demo` is a convenience for reviewers - it keeps demo data separate and auto-creates demo habits without prompting.
  - You may set the environment variable `MOMENTUM_DEMO_DB` to change the demo DB filename used by `--demo`.

**Recommended workflow for reviewers**

1. (Optional) Rebuild the environment and install dependencies.
2. Seed the demo DB: ``python scripts/seed_demo_db.py --overwrite``
3. Launch the app in demo mode: ``python momentum_main.py --demo``
4. Explore the UI/CLI; create, modify, and complete habits - demo DB stays isolated.

**Commands to commit & push changes (optional, for observing CI):**

```powershell
git add momentum_main.py USAGE.md scripts/seed_demo_db.py
git commit -m "ci: add demo-mode CLI and usage docs; seed script for CI/local demo"
git push origin main

# Watch the latest workflow run
gh run list --repo aaronmalunga/momentum-hub --limit 5
gh run watch <run-id> --repo aaronmalunga/momentum-hub
```
