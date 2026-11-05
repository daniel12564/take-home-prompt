# DASH-247: "Is this normal for us?"

A single-page Relay dashboard for a Customer Admin. It compares last week's calls, leads and appointments against what is typical for the Account (or one Location), and lists the Locations that need attention with a plain-language reason. Vocabulary (Account, Location, Reporting Week, Baseline, Finding) is in [`GLOSSARY.md`](GLOSSARY.md).

## 1. How to run it

Requirements: Docker with Compose. Nothing else is installed on the host.

```sh
cp .env.example .env   # optional: Compose falls back to the same defaults
make up                # builds and starts db (Postgres 16), api (Django) and web (Vite)
make setup             # runs migrations and loads the seed (20 Accounts, 12,626 Activity Events)
```

Open <http://localhost:5173>. The API is at <http://localhost:8000/api/v1/>. The first build should take a few minutes.

### Database setup

- **With Docker**, the `db` service creates the `relay` user, password and database on first start. Data lives in the `db-data` volume. `make setup` creates the schema and loads the seed.

### Environment variables

All have defaults, so `.env` is optional.

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `postgres://relay:relay@db:5432/relay` | Database connection. Outside Docker the default is `localhost:5432`. |
| `DJANGO_SECRET_KEY` | `insecure-dev-key-change-me` | Django secret key. Dev only. |
| `DJANGO_DEBUG` | `true` | Django debug mode. |
| `VITE_API_BASE_URL` | `/api/v1` | API base path used by the frontend. |
| `API_PORT` | `8000` | Host port for the API. |
| `WEB_PORT` | `5173` | Host port for the web app. |
| `API_PROXY_TARGET` | `http://api:8000` (set by Compose) | Where the Vite dev server proxies `/api`. Defaults to `http://localhost:8000` outside Docker. |

If a port is taken: `API_PORT=8018 WEB_PORT=5188 make up`.

### Commands

| Command | What it does |
|---|---|
| `make up` | Build and start `db`, `api` and `web` in the background |
| `make setup` | Migrate and load the seed (safe to repeat) |
| `make test-api` | Backend tests (`pytest`) in a container |
| `make test-web` | Frontend tests (Vitest + Testing Library) in a container |
| `make down` | Stop everything **and delete the database volume**. Run `make setup` again after the next `make up`. |

### What to look at

The dashboard treats **2026-07-27** as "today", because the seed ends that day (`DASHBOARD_REFERENCE_DATE` in `backend/config/settings/base.py`). Try these views:

- **Account 6 (Metro Collision Centers), week of 1 Jun:** one Account-wide critical Finding, concentrated on Wed 3 Jun, instead of 15 identical cards.
- **Account 15 (Sierra Pest Solutions), default week:** `Site B` has 0 calls vs 5 typical (`critical`).
- **Account 20 (Quiet Harbor Spa):** grey everywhere, "no activity recorded".

The full row-by-row checklist is in [`PLAN_REFINED.md` §3.13](PLAN_REFINED.md).

## 2. How I read the ticket

DASH-247 asks the dashboard to let a customer answer *"is this normal for us?"* at a glance, without exporting data or calling their account manager. Product's hints are a baseline, multi-location customers, and a Customer Admin acting on it on a Monday morning. `PROJECT_BACKGROUND.md` adds the two pains: *"is this number normal?"* and *"which location needs attention?"*

I turned that into two questions and one screen:

1. **Is last week typical?** The Activity Summary shows each Metric (calls received, leads created, appointments set) next to its Baseline, with a colour-coded Status.
2. **Which Locations need attention, and why?** The Attention List shows only deviations, each with a one-sentence explanation. When most Locations move together, it shows one Account-wide Finding.

"This week" means the last **complete** Monday to Sunday week, so Monday morning shows the week that just ended. Verdicts are deterministic. Alerting and forecasting are out of scope per the ticket. Auth, production infra and visual polish are out of scope per the brief.

## 3. Key assumptions and design decisions

| Decision | Why | Trade-off weighed |
|---|---|---|
| **Fixed Reference Date (2026-07-27)** instead of `today()` | The seed ends on that date. With the real date the dashboard would be empty. | The demo is reproducible, but it is not "live". Swapping in `today()` is a one-line change. |
| **Weekly granularity**, complete Mon–Sun weeks in the Account's timezone | "Typical" is well defined week over week. A half-week judged against full weeks would mislead. | No daily or custom-range views. Timezone handling adds code, but a Sunday 23:30 Chicago event correctly belongs to the earlier week. |
| **Baseline = median of the 8 prior complete weeks** (minimum 4) | Per-Location weekly counts are tiny (1–5), and Account 6 has a one-day spike 10× normal. A mean would be poisoned for the whole window. | The median ignores one outlier week. The cost is that the first 4 weeks of history show `insufficient_data` instead of a guess. |
| **Combined Tolerance** `max(3, 0.30 × baseline, 1.5 × √baseline)` | A percentage alone flags 3→1 swings that are noise. A z-score on 8 points is unstable. The absolute floor and √ term quiet small counts. The relative term scales for big Accounts. | Fewer false alarms, but the constants are tuned to this seed's volumes. They live together in `DASHBOARD_RULES`. See [ADR-0001](docs/adr/0001-median-baseline-with-combined-tolerance.md). |
| **Account-wide Finding** when at least 3 Locations *and* at least half deviate the same way | The seeded spike hits all 15 Locations at once. A flat list would be 15 identical cards. | The summary is more useful, but the sentence quotes Account totals rather than the sum of affected Locations. This matches the Summary card. |
| **No-activity Finding** for a Location that is silent | A Location at zero is the most actionable signal. It replaces its per-Metric Findings. | Needs a "Location universe" (any event in the window or viewed week). Locations are free text on the event. |
| **Deterministic template explanations, no LLM** | The ticket allows an LLM, but it would put a network call, an API key and non-deterministic text behind a verdict the admin must trust at a glance. | Less fluent prose. Explanations are golden-string testable. A future LLM layer reads Findings and never decides what is abnormal. See [ADR-0002](docs/adr/0002-deterministic-findings-without-llm.md). |
| **Account selector in the header**, with the Account id in every API path | There is no login, and the demo needs a 15-Location, single-Location and no-data Account. | Not a real identity model. It is explicit and easy to replace with auth. |
| **No `Location` table**, only free text on the event | The seed has no Location entity. | Less schema, but no Location attributes. A rename would split history. |
| **Pure rules modules, no ORM** (`periods`, `baseline`, `rules`, `findings`, `explanations`) | The normality logic is the only risky part. This makes it testable with hand-built inputs. | Slightly more plumbing. One grouped query per endpoint feeds the pure code, so there is no N+1. |
| **Tests at three seams**: HTTP API on a handcrafted fixture, pure services, React components | They check observable behaviour on small inputs with known answers. | The full seed is checked by a manual checklist, not automatically. |
| **Selector state in URL params** (`?account=&week=&location=`) | Views can be bookmarked and shared. | The URL has to be validated on load. |

## 4. What I deliberately deferred, and why

- **Authentication.** Out of scope per the brief. A trusted admin and the Account selector are enough to demo the logic.
- **LLM-written explanations.** Allowed, but templates give determinism and testability first. The structured Finding is the contract for adding one later.
- **Alerting, notifications and forecasting.** Out of scope per the ticket. Seasonal or weekday-adjusted Baselines are forecasting-adjacent and unneeded for "is this typical?".
- **Outcome and duration Metrics** (missed-call rate, conversion, call length). They are loaded but unused. Counts answer the ticket, and no outcome anomalies exist in the seed.
- **Custom date ranges, partial weeks and daily views.** They add complexity and weaken the Baseline's meaning.
- **A per-Location breakdown in the Activity Summary.** The Location selector and the Attention List cover it.
- **End-to-end browser tests and automated tests against the full seed.** The highest-risk logic is unit-tested. The seed is verified by the manual checklist in `PLAN_REFINED.md` §3.13.
- **Production infra, CI and visual polish.** Out of scope per the brief.

## 5. What I'd do with another day

1. **Automate the seed acceptance checklist** as a test that loads the CSVs and asserts the Account 6, 15, 16 and 20 verdicts, so a retune of `DASHBOARD_RULES` can't silently change them.
2. **Retune and validate the constants** against real volumes. Today a quiet Location with Baseline 0 is flagged `above` from 3 events, which produces a few low-severity warnings.
3. **Replace the fixed Reference Date** with the real date, and add a seed refresh or ingestion path so the dashboard isn't empty.
4. **Add a few Playwright smoke tests** for the three selectors and the URL state, with CI running `make test-api` and `make test-web`.
5. **Add an optional LLM rewrite layer** behind a flag. It would take structured Findings, fall back to the template text, and never change a verdict.
6. **Add a per-Location comparison view** in the Activity Summary, plus a drill-down into the day-level events behind an Account-wide Finding.
7. **Add real auth**, and make the Account selector reflect the signed-in user's Accounts.

## Further reading

- [`GLOSSARY.md`](GLOSSARY.md): domain language.
- [`docs/adr/`](docs/adr/): the two decisions that shape the rules.
- [`PLAN_REFINED.md`](PLAN_REFINED.md): decisions, API contract, test plan and acceptance checklist. [`PLAN.md`](PLAN.md) is the original plan.
- [`TICKET.md`](TICKET.md) and [`PROJECT_BACKGROUND.md`](PROJECT_BACKGROUND.md): the source brief.