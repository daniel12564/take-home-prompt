# 01: Runnable skeleton with API envelope and both test harnesses

**What to build:** A developer can clone the repo, run `make up`, open the web app in a browser and see it successfully call the API; `make test-api` and `make test-web` each run one passing test. Nothing domain-specific yet: this ticket makes every later slice cheap to land.

Spec: `.scratch/dash-247-is-this-normal/spec.md`. Decisions: `PLAN_REFINED.md` §3.9 (envelopes), §3.10 (layout), §3.11 (tooling).

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] Docker Compose defines `db` (Postgres 16), `api` (Python 3.12, Django 5, DRF, psycopg 3, managed with `uv`, command is the dev server) and `web` (Node 20, Vite dev server proxying `/api` to `api`).
- [ ] Makefile targets exist and work: `up`, `down` (removes volumes), `setup` (migrate then seed; the seed command may be a no-op stub until ticket 02), `test-api`, `test-web`.
- [ ] `.env.example` lists `DATABASE_URL`, `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `VITE_API_BASE_URL`; settings are split into base and development and read from the environment.
- [ ] Backend layout follows the repo's backend rules: a `config` package, a `core` package with the unified response helpers and a global DRF exception handler, a versioned API package, and `accounts` / `activity` app packages (models may be empty).
- [ ] Every API response uses the unified envelope: success is `{ "success": true, "data": ... }`; failure is `{ "success": false, "message", "errors", "error_code" }`. Unknown routes and validation failures already come back in that shape with `NOT_FOUND` / `VALIDATION_ERROR`.
- [ ] A trivial versioned endpoint (for example a health or root endpoint) returns the success envelope and is covered by one DRF test-client test using `pytest` + `pytest-django`.
- [ ] Frontend is Vite + React + TypeScript + Tailwind + TanStack Query, single quotes, 2-space indent, kebab-case files; a query client is configured and the page renders the result of the trivial endpoint with loading and error states.
- [ ] One Vitest + Testing Library test renders the page and passes.
- [ ] No router, global store, form library or component kit is added.
