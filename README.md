# Relay reporting dashboard: "is this normal for us?"

A single-page dashboard for a Relay **Customer Admin**. It answers two questions on a Monday morning:

1. **Is last week's activity typical for us?** The *Activity Summary* shows calls received, leads created and appointments set for the Account (or one Location), each next to what is typical and colour-coded.
2. **Which Locations need attention, and why?** The *Attention List* lists only the deviations, each with a plain-language explanation. When most Locations move together it shows one Account-wide Finding instead of a wall of identical cards.

Verdicts are deterministic: no LLM, no alerting, no forecasting. Vocabulary (Account, Location, Reporting Week, Baseline, Finding, ...) is defined in [`GLOSSARY.md`](GLOSSARY.md).

## Run it

Requirements: Docker with Compose. Nothing else is installed on the host.

```sh
cp .env.example .env     # optional: Compose falls back to the same defaults without it
make up                  # builds and starts db, api (Django) and web (Vite)
make setup               # migrates and loads the seed (20 Accounts, 12,626 Activity Events)
```

Then open <http://localhost:5173> (API at <http://localhost:8000/api/v1/>). The first load takes a few minutes while images build.

If 8000 or 5173 are taken, set `API_PORT` and `WEB_PORT` in `.env` (or on the command line: `API_PORT=8018 WEB_PORT=5188 make up`).

| Command | What it does |
|---|---|
| `make up` | Build and start `db`, `api` and `web` in the background |
| `make setup` | Run migrations and load the seed; safe to repeat (skips when Accounts exist) |
| `make test-api` | Backend tests (`pytest`) in a container |
| `make test-web` | Frontend tests (Vitest + Testing Library) in a container |
| `make down` | Stop everything **and delete the database volume**; run `make setup` again after the next `make up` |

To reload the seed from scratch without tearing down: `docker compose run --rm api uv run python manage.py seed_activity --flush`.

## Using the dashboard

Three selectors in the header, all reflected in the URL (`?account=6&week=2026-06-01&location=Site+B`) so a view can be bookmarked or shared:

- **Account**: there is no login, so switch customers here. Shows each Account's name and Location count. Changing it clears the Location and keeps the week.
- **Week**: any complete Monday to Sunday Reporting Week, in the Account's own timezone, from 2 Feb to 20 Jul 2026. It opens on the last complete week before the Reference Date (20 Jul). The in-progress week is not offered.
- **Location**: the whole Account, or one Location (every Location the Account has ever had activity at).

**Status colours** (Activity Summary cards):

| Colour | Status | Meaning |
|---|---|---|
| Green | `typical` | Within Tolerance of the Baseline |
| Amber | `above` | Higher than typical: worth a look, not phrased as a problem |
| Red | `below` | Lower than typical |
| Grey | `insufficient_data` | Cannot be judged: either fewer than 4 weeks of history, or no activity recorded at all (the card says which) |

**Severity** (Attention List): `critical` is a Location with no activity at all, a Metric that fell to zero from a Baseline of 3 or more, or a deviation of at least twice the Tolerance, and also any Account-wide Finding that includes one. Everything else is a `warning`. The list shows Account-wide Findings first, then critical, then warning, larger deviations first.

### Rules in one paragraph

A Metric's **Baseline** is the median of that Metric over the 8 complete weeks before the viewed one (at least 4 are required; the first 4 weeks of data show `insufficient_data`). The Account's Baseline is the median of weekly sums. A Metric is `typical` unless it deviates from its Baseline by at least `max(3, 0.30 × baseline, 1.5 × √baseline)`. A Location with Baseline activity but no events at all in the viewed week gets a single No-activity Finding. When at least 3 Locations *and* at least half of the Account's Locations deviate in the same direction on a Metric, those Findings collapse into one Account-wide Finding; if more than 60% of that week's events for those Metrics fall on one local day, the explanation names the day. Reasons: [ADR-0001](docs/adr/0001-median-baseline-with-combined-tolerance.md) and [ADR-0002](docs/adr/0002-deterministic-findings-without-llm.md).

### The fixed Reference Date, and what to look at in the seed

The dashboard treats **2026-07-27** as "today" because the seed data ends on that date; with the real date the dashboard would be empty. It is `DASHBOARD_REFERENCE_DATE` in `backend/config/settings/base.py` (the frontend mirrors it in `frontend/src/lib/weeks.ts`).

| View | What you should see |
|---|---|
| Account 6 (Metro Collision Centers, 15 Locations), week of 1 Jun | One Account-wide critical Finding, concentrated on Wed 3 Jun, instead of 15 cards |
| Account 6, week of 29 Jun | The spike does not poison the Baseline; `Site G` shows a No-activity Finding |
| Account 15, default week | `Site B` calls 0 vs 5 typical, `critical` |
| Account 20 (Quiet Harbor Spa) | Grey everywhere, "no activity has been recorded for this account yet" |
| Account 16 (one Location), default week | All `typical`, nothing to report |
| Account 1, week of 16 Feb | Grey "not enough history yet" (only 2 weeks of history) |

The full row-by-row list, with exact numbers, is the manual acceptance checklist in [`PLAN_REFINED.md` §3.13](PLAN_REFINED.md).

## Where things live

- **Rule constants**: `DASHBOARD_RULES` in `backend/config/settings/base.py`, next to the Reference Date. The rules code (`backend/activity/services/`) takes it as an argument and defines no constants of its own.
- **Pure normality logic** (no database): `backend/activity/services/{periods,baseline,rules,findings,explanations}.py`. Only `dashboard.py` and `managers.py` touch the ORM.
- **API**: `GET /api/v1/accounts/`, `.../accounts/{id}/locations/`, `.../accounts/{id}/dashboard/activity-summary/?week_start=&location=`, `.../accounts/{id}/dashboard/attention/?week_start=`. Every response uses one envelope: `{success, data}` or `{success: false, message, errors, error_code}`.
- **Frontend**: `frontend/src/features/dashboard/`, with selector state in URL search params (`frontend/src/lib/url-state.ts`).
- **Seed**: `backend/seed/` holds the source `seed.txt`, the one-off `convert_seed.py` and the two committed CSVs that `seed_activity` loads.

## Further reading

- [`GLOSSARY.md`](GLOSSARY.md): the domain language used in code, UI and docs.
- [`docs/adr/`](docs/adr/): the two decisions that shape the rules.
- [`PLAN_REFINED.md`](PLAN_REFINED.md): decisions, API contract, test plan and acceptance checklist ([`PLAN.md`](PLAN.md) is the original plan, kept for comparison).
- [`.scratch/dash-247-is-this-normal/spec.md`](.scratch/dash-247-is-this-normal/spec.md): the spec with user stories and out-of-scope list.

## Known limitations

These are deliberate for this version (see [`PLAN_REFINED.md` §5](PLAN_REFINED.md)).

- **No authentication.** One trusted Customer Admin; the Account selector stands in for a login.
- **No LLM.** Explanations are templates rendered from structured Findings.
- **Counts only.** Outcome and duration are stored but unused; there are no rates, conversions or call lengths.
- **Tests are unit and fixture-level.** Pure rules are tested without a database, the API on a small handcrafted fixture, and the UI with component tests. There are no end-to-end browser tests and no automated tests against the full seed; the seed expectations are the manual checklist.
- **Constants are tuned to the seed.** Typical weekly counts there are 3 to 5 calls per Location. Retune `DASHBOARD_RULES` for different volumes. One consequence: a quiet Location with a zero Baseline is flagged `above` from 3 events in a week, which produces a few low-severity warnings.
- **Fixed Reference Date and weekly granularity.** No custom date ranges, partial weeks, or daily views.
- **Account-wide Finding numbers are Account totals.** When only some Locations deviate, the sentence still quotes the whole Account's total and Baseline (matching the Activity Summary card) beside the count of affected Locations.
- **No per-Location breakdown in the Activity Summary.** Pick a Location in the selector, or read the Attention List.
