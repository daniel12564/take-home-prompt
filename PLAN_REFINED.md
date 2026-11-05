# Refined plan — DASH-247 "Is this normal for us?"

Refined from `PLAN.md` after a grilling session on 2026-11-05. `PLAN.md` is kept as the original for comparison. Vocabulary follows `GLOSSARY.md`; decisions that meet the ADR bar are in `docs/adr/`.

## 1. Changes from PLAN.md and why

| PLAN.md said | Refined plan says | Why |
|---|---|---|
| "current week", date range selector | Fixed **Reference Date** `2026-07-27`; **week picker** over complete Mon–Sun Reporting Weeks | Seed data ends 2026-07-27; "typical" is only well-defined week-over-week |
| compare against "typical numbers" | **Baseline** = median of trailing 8 complete weeks; explicit **Tolerance** formula | Per-location weekly counts are 1–5; percentages alone flag noise; account 6 has a 10× one-day spike that would poison a mean |
| LLM writes explanations | **No LLM.** Deterministic templates from structured Findings | Ticket makes it optional; it was never going to be implemented |
| hardcoded identity | **Account selector** in the header; account id in every API path | Lets the demo cover 15-location, single-location and no-data accounts |
| per-location issue list | Per-location Findings **plus Account-wide Findings** and a "no activity" Finding | The seeded spike hits all 15 locations at once; a flat list would be 15 identical cards |
| `seed.sql` management command | `seed.txt` → two CSVs → `seed_activity` with `bulk_create` | File is `seed.txt`; CSV + ORM keeps ids, sequences and schema under Django's control |
| build filters/UI early | Rules engine first, tested without a DB | The normality logic is the only risky part |
| full frontend stack | Vite + React + TS + TanStack Query + Tailwind only | One page, two sections, three selectors |

## 2. Fixed facts about the data

- 20 Accounts, 12,626 Activity Events, `2026-02-01` → `2026-07-27 22:20 UTC`. Account 20 has no events.
- Locations per Account: 1 to 15 (`Site A` … `Site O`), free-text on the event.
- Volumes are small: median per (Location, Event Type) per week is 3–5 calls, 1–3 leads, 0–2 appointments.
- Planted signals: account 6, **2026-06-03** — 805 events in one day across all 15 Locations; `6/Site G` dark in weeks of 04-13 and 06-29; `6/Site N` dark 02-23; `18/Site C` dark 03-23; `15/Site B` zero calls in the week of 07-20 (Baseline 5).
- No Outcome-rate anomalies exist in the data.

## 3. Decisions

### 3.1 Scope

- One page: **Activity Summary** + **Attention List**.
- Selectors: Account, Reporting Week, Location. All three live in URL search params (`?account=6&week=2026-07-20&location=Site+B`). Changing Account clears `location`, keeps `week`.
- Out: auth, LLM, alerting, Outcome-based Metrics, forecasting, production infra, visual polish.

### 3.2 Time

- **Reference Date**: constant `DASHBOARD_REFERENCE_DATE = date(2026, 7, 27)` in settings.
- **Reporting Week**: Monday 00:00 → next Monday 00:00 in the Account's IANA timezone, converted to UTC for querying.
- Default week = last complete week before the Reference Date (`2026-07-20` … `07-26`).
- Week picker: every complete week from `2026-02-02` to `2026-07-20`. The in-progress week is not selectable.

### 3.3 Metrics

Three counts per scope per Reporting Week: `call_received`, `lead_created`, `appointment_set`. Scope is the whole Account or one Location.

### 3.4 Baseline

- Baseline Window = the 8 complete Reporting Weeks immediately before the viewed one, clipped at `2026-02-02`.
- Baseline = **median** of the Metric over the window. Account scope uses the median of weekly **sums**.
- Fewer than 4 weeks in the window → `insufficient_data` (affects weeks before `2026-03-02`).
- An Account with no Activity Events in the window ∪ viewed week → `insufficient_data` for every Metric and an empty Attention List with an explanatory empty state (account 20).

### 3.5 Status and Tolerance

```python
DASHBOARD_RULES = {
    'baseline_weeks': 8,
    'min_baseline_weeks': 4,
    'tolerance_abs_min': 3,
    'tolerance_rel': 0.30,
    'tolerance_sqrt_factor': 1.5,
    'critical_tolerance_multiple': 2,
    'rollup_min_locations': 3,
    'rollup_min_share': 0.5,
    'one_day_concentration_share': 0.6,
}
```

- `tolerance = max(abs_min, rel * baseline, sqrt_factor * sqrt(baseline))`
- `|current - baseline| < tolerance` → `typical`; otherwise `above` / `below`.
- Baseline 0 and current 0 → `typical`. Baseline 0 and current ≥ 3 → `above`.
- Severity: `critical` when `|current - baseline| >= 2 * tolerance` or (`current == 0` and `baseline >= 3`); else `warning`.
- Colours: `typical` green, `below` red, `above` amber, `insufficient_data` grey. `above` is attention-worthy but not phrased as a problem.

Worked examples: baseline 4 → tolerance 3 → flags at ≤1 or ≥7. Baseline 40 → tolerance 12 → flags at ≤28 or ≥52.

### 3.6 Findings

Location universe for a week = Locations with any Activity Event in the Baseline Window ∪ viewed week. The Location selector lists all-time distinct names.

1. **No-activity Finding**: Location in the universe with zero events of any type in the viewed week → one `critical` Finding, and no per-Metric Findings for that Location.
2. **Per-Location Finding**: one per (Location, Metric) whose Status is not `typical`.
3. **Account-wide Finding**: for each (Metric, direction), if at least `rollup_min_locations` Locations **and** at least `rollup_min_share` of the universe have that Status, emit one Account-wide Finding and drop those per-Location Findings. Locations deviating the other way stay listed. Accounts with fewer than 3 Locations never roll up. Account-wide Findings in the same direction across several Metrics merge into one Finding listing the Metrics.
4. **One-day concentration**: for an Account-wide Finding only, if more than `one_day_concentration_share` of the week's events for that Metric fall on a single local day, name that day in the explanation.

Finding object (the contract between rules, API, UI and tests):

```python
@dataclass(frozen=True)
class Finding:
    scope: Literal['account', 'location']
    location: str | None
    kind: Literal['metric', 'no_activity']
    event_types: tuple[str, ...]      # one for per-Location, one or more for Account-wide
    direction: Literal['above', 'below']
    severity: Literal['warning', 'critical']
    current: int
    baseline: float | None
    delta_pct: float | None
    affected_locations: int | None    # Account-wide only
    total_locations: int | None       # Account-wide only
    concentrated_on: date | None      # Account-wide only
    explanation: str                  # rendered from the fields above, never the reverse
```

Attention List order: Account-wide first, then `critical`, then `warning`; within a tier by `|delta_pct|` descending; no cap.

Explanation templates (one per `kind` × `scope`), e.g.

- per-Location metric: `Site B received 0 calls this week; it typically receives about 5.`
- no activity: `Site G recorded no calls, leads or appointments this week; it is normally active.`
- Account-wide: `Calls, leads and appointments were far above typical at 14 to 15 of 15 locations (529 calls vs about 40.5). Most of this week's events happened on Wed 3 Jun.` The numbers are the Account's own, identical to the Activity Summary card (viewed-week total vs median of weekly sums), not a sum over the affected Locations; the Finding's `affected_by_metric` carries the per-Metric Location counts.

### 3.7 Data model

```python
class Account(models.Model):          # db_table = 'accounts'
    name, industry, timezone (IANA string), created_at

class ActivityEvent(models.Model):    # db_table = 'activity_events'
    account = FK(Account, on_delete=PROTECT)
    location = CharField
    event_type = CharField(choices=EventType)
    occurred_at = DateTimeField        # UTC
    duration_seconds = IntegerField(null=True)
    outcome = CharField(choices=Outcome, null=True)
    # indexes: (account, occurred_at), (account, location, event_type, occurred_at)
```

No `Location` model. `outcome` and `duration_seconds` are stored, validated by choices, and otherwise unused.

### 3.8 Seed

- `backend/seed/convert_seed.py`: one-off that parses `backend/seed/seed.txt` into `accounts.csv` and `activity_events.csv` (empty cell = NULL). Script, source file and CSVs are all committed.
- `python manage.py seed_activity [--flush]`: reads the CSVs, `bulk_create(batch_size=1000)` inside `transaction.atomic()`, preserves ids, resets both sequences, skips when `accounts` already has rows unless `--flush`.

### 3.9 API

Base path `/api/v1/`. Read-only. Unified envelopes from `core/responses.py` and `core/exceptions.py`:

```json
{ "success": true,  "data": { ... } }
{ "success": false, "message": "...", "errors": { "week_start": ["..."] }, "error_code": "VALIDATION_ERROR" }
```

| Endpoint | Query | Returns |
|---|---|---|
| `GET accounts/` | — | `[{ id, name, timezone, location_count }]` |
| `GET accounts/{id}/locations/` | — | `[ "Site A", ... ]` (all-time distinct, sorted) |
| `GET accounts/{id}/dashboard/activity-summary/` | `week_start?`, `location?` | see below |
| `GET accounts/{id}/dashboard/attention/` | `week_start?` | `{ account_id, week_start, week_end, insufficient_reason, findings: [Finding] }` |

Activity Summary payload:

```json
{
  "account_id": 6,
  "week_start": "2026-07-20", "week_end": "2026-07-26",
  "location": null,
  "baseline_weeks_used": 8,
  "insufficient_reason": null,
  "metrics": [
    { "event_type": "call_received", "current": 51, "baseline": 42.0,
      "delta": 9, "delta_pct": 21.4, "status": "typical" }
  ]
}
```

`insufficient_reason` (both endpoints) is `null` when verdicts can be given, `no_events` when the scope recorded no Activity Event in the Baseline Window or viewed week (e.g. account 20), and `short_history` when events exist but the window holds fewer than 4 weeks. The UI uses it to word the empty states differently (spec story 8).

Errors: unknown account → 404 `NOT_FOUND`; `week_start` not a Monday, before `2026-02-02`, or not complete at the Reference Date → 400 `VALIDATION_ERROR`; unknown `location` for the account → 400.

### 3.10 Code layout

```
backend/
  pyproject.toml  (uv)            frontend/
  config/settings/{base,development}.py     src/
  config/urls.py                              api/{client.ts,accounts.ts,dashboard.ts}   # fetchers + TanStack hooks
  core/{responses,exceptions}.py              features/dashboard/
  accounts/{models,admin}.py                    dashboard-page.tsx
  activity/{models,managers,admin}.py           account-selector.tsx
  activity/services/periods.py                  week-picker.tsx
  activity/services/baseline.py                 location-selector.tsx
  activity/services/rules.py                    activity-summary.tsx
  activity/services/findings.py                 attention-list.tsx
  activity/services/explanations.py             status-badge.tsx
  activity/services/dashboard.py   # DB entry point: aggregation → rules → payloads
  activity/management/commands/seed_activity.py lib/url-state.ts
  api/v1/urls.py                                lib/types.ts
  api/v1/accounts/{urls,views,serializers}.py
  api/v1/dashboard/{urls,views,serializers}.py
  seed/{seed.txt,convert_seed.py,accounts.csv,activity_events.csv}
  tests/conftest.py                # handcrafted fixture factory (3.12)
  tests/unit/  tests/api/
docker-compose.yml   Makefile   .env.example
```

- `periods`, `baseline`, `rules`, `findings`, `explanations` are pure functions over plain data; only `dashboard.py` and `managers.py` touch the ORM.
- `managers.py`: `ActivityEventQuerySet.weekly_counts(account, week_starts, location=None)` using `TruncWeek('occurred_at', tzinfo=ZoneInfo(account.timezone))`, `values('location', 'event_type', 'week').annotate(n=Count('id'))`; one extra `TruncDay` query only when an Account-wide Finding needs the one-day callout.
- Views parse params with a serializer, call one service function, wrap in the envelope.
- TanStack query keys: `['accounts']`, `['locations', accountId]`, `['summary', accountId, week, location]`, `['attention', accountId, week]`.

### 3.11 Tooling

- Python 3.12, Django 5.x, DRF, psycopg 3, `uv`. Node 20, Vite, `npm`.
- `docker-compose.yml`: `db` (postgres:16), `api` (command: `runserver 0.0.0.0:8000`), `web` (Vite dev server, `/api` proxied to `api`).
- `.env.example`: `DATABASE_URL`, `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `VITE_API_BASE_URL`.
- Makefile:

```make
up:        docker compose up -d db api web
down:      docker compose down -v
setup:     docker compose run --rm api uv run python manage.py migrate && \
           docker compose run --rm api uv run python manage.py seed_activity
test-api:  docker compose run --rm api uv run pytest
test-web:  docker compose run --rm web npm test
```

### 3.12 Tests

Backend unit tests, `pytest` + `pytest-django`, no database access:

- `periods`: week boundaries for `America/Chicago`, `America/Phoenix`, `UTC`; Sunday 23:30 local stays in the week; default week from Reference Date; picker range; rejection of non-Monday / incomplete weeks.
- `baseline`: median over 8; clipping at data start; `< 4` weeks → insufficient; a single 10× week does not move the median; account-level sums.
- `rules`: tolerance table (baselines 0, 1, 3, 4, 10, 40); `typical` at 3→1 is **not** flagged (noise guard); 5→0 is `critical`; 0→3 is `above warning`; account with no events → `insufficient_data`.
- `findings`: no-activity suppresses per-Metric Findings; rollup at 3/5 fires, 2/5 doesn't, 1-Location Accounts never roll up; opposite-direction Locations survive the rollup; multi-Metric same-direction merge; ordering.
- `explanations`: one golden string per template, including the one-day callout.

Backend API tests, DRF `APIClient` against the test database, on one handcrafted fixture built in `tests/conftest.py` (a factory, not the seed CSVs):

- Fixture: Account `A` in `America/Chicago` with Locations `North`, `South`, `East`; Account `B` in `UTC` with no Activity Events. Ten Reporting Weeks ending at the default week, steady volumes per Location (about 5 calls, 2 leads, 1 appointment a week), plus three planted signals: `South` has zero events in the default week; `North` has 11 calls in the default week (12 would be `critical` under the severity rule in 3.6: |12 − 5| = 7 ≥ 2 × tolerance 3; 11 gives 6 < 2 × 3 → `warning`); all three Locations have 4× calls in week 6 (an Account-wide spike that must not move later Baselines).
- `accounts/`: both Accounts, `location_count` 3 and 0.
- `accounts/{id}/locations/`: sorted names; 404 for an unknown id.
- `activity-summary/`: default week when `week_start` omitted; `location=North` calls `above`; Account totals use weekly sums; `baseline_weeks_used` is 8; Account `B` returns `insufficient_data` for every Metric; `week_start` before `2026-02-02`, a non-Monday, or `2026-07-27` → 400 `VALIDATION_ERROR` with the field in `errors`; unknown `location` → 400.
- `attention/`: default week yields exactly a `critical` No-activity Finding for `South` and a `warning` Finding for `North`, ordered critical first; week 6 yields one Account-wide Finding and no per-Location Findings; Account `B` yields an empty list; response envelopes match `core/responses.py`.
- Timezone: one event at Sunday 23:30 `America/Chicago` (Monday 04:30/05:30 UTC) is counted in the earlier week.
- Query budget: `activity-summary/` and `attention/` each run a bounded number of queries (`django_assert_num_queries`) so the per-Location work never becomes N+1.

Frontend, Vitest + RTL: `status-badge` colour mapping; Activity Summary and Attention List empty / insufficient states.

### 3.13 Manual acceptance checklist (from the seed, verified against the running app)

Run after `make up && make setup`. Each row lists the **complete** Attention List for that view (verified with curl against the real seed, ticket 08). An earlier draft of the 06-29, 04-13 and 03-02 rows named only the headline Findings; the extra per-Location `warning`s now listed are correct outputs of the ADR-0001 rules, checked against the raw events (e.g. `Site O` calls 6 vs a median of 3: deviation 3 = tolerance 3, so it is flagged; a Location at Baseline 0 with 3 events is `above`). They are small-count blips, not bugs.

| Account / week | Expected |
|---|---|
| 6, `2026-07-20` (default) | Summary: calls 51 vs 42 typical, leads 17 vs 15 typical, appointments 19 vs 13 **above**. Attention: 3 `warning` Findings (`Site A` calls 7 vs 4, `Site H` calls 6 vs 2.5, `Site M` appointments 3 vs 0). |
| 6, `2026-06-01` | Summary: all three Metrics `above`, calls 529 vs 40.5. Attention: **one** `critical` Account-wide Finding (calls 15/15, leads 15/15, appointments 14/15; 529 calls vs about 40.5, the same numbers as the Summary card; concentrated on 2026-06-03), nothing per-Location. |
| 6, `2026-06-29` | Summary all `typical`; Baseline unaffected by the spike (calls 46.5). Attention: `Site G` no-activity `critical`; `warning`s `Site H` leads 3 vs 0, `Site E` calls 8 vs 4.5. |
| 6, `2026-04-13` | Summary calls and appointments `below`, leads `typical`. Attention: `Site G` no-activity `critical`, `Site N` calls 0 vs 3.5 `critical`; `warning`s `Site F` leads 3 vs 0, `Site O` calls 6 vs 3. |
| 15, `2026-07-20` | `Site B` calls 0 vs 5 `critical`; `Site C` calls 6 vs 2.5 `warning`; account totals typical. |
| 20, any week | All Metrics `insufficient_data` (`insufficient_reason: no_events`); the cards and the empty Attention List both say no activity has been recorded for the account, not that history is short. |
| 1, `2026-02-16` | `insufficient_data` everywhere (only 2 baseline weeks; `insufficient_reason: short_history`, cards and Attention List say more history is needed). |
| 1, `2026-03-02` | First week with verdicts (4 baseline weeks), all `typical`; `warning`s `Site E` appointments 4 vs 1, `Site F` leads 4 vs 1. |
| 16, `2026-07-20` | Single Location, ~6 events/week: everything `typical`, empty Attention List (noise guard). |
| any | `week_start=2026-07-27`, a non-Monday, a week before `2026-02-02`, an unparseable date and an unknown `location` are rejected with 400 `VALIDATION_ERROR` naming the field; unknown account 404 `NOT_FOUND`. |

## 4. Build order

Each step ends with its check passing before the next starts.

1. **Scaffold**: `backend/` (uv, Django, DRF, settings split, `core/`), `frontend/` (Vite TS template, Tailwind, TanStack Query), Compose, Makefile, `.env.example`. Check: `make up` serves a DRF root and a Vite page.
2. **Models and seed**: `Account`, `ActivityEvent`, migrations, `convert_seed.py`, CSVs, `seed_activity`. Check: `make setup` loads 20 / 12,626 rows, idempotent, `--flush` reloads, admin lists both.
3. **Pure rules engine + unit tests**: `periods`, `baseline`, `rules`, `findings`, `explanations`, `DASHBOARD_RULES`. Check: `make test-api` green with the matrix in 3.12.
4. **Aggregation and API**: `managers.weekly_counts`, `services/dashboard.py`, the four endpoints, serializers, envelopes, error codes, the handcrafted fixture and the API tests in 3.12. Check: `make test-api` green, then `curl` through the acceptance table in 3.13.
5. **Dashboard UI**: URL state, three selectors, Activity Summary with Status colours, Attention List with Severity, loading / empty / insufficient / error states. Check: the acceptance table by eye; `make test-web` green.
6. **Wrap-up**: README with `make` workflow, known limitations (unit tests only, fixed Reference Date, counts only), and the decisions pointer to `docs/adr/`.

## 5. Known limitations (deliberate)

- Reference Date is fixed; swapping it for `today()` is a one-line change but the seed would then show no data.
- No end-to-end tests and no tests against the full seed; API tests run on a small handcrafted fixture, and the seed signals in 3.13 remain a manual checklist.
- Outcome and duration data are loaded but not surfaced.
- A Location with a zero Baseline is flagged `above` from 3 events in a week (e.g. 3 leads at a site that normally has none). This is the ADR-0001 absolute allowance working as specified; it produces a few low-severity `warning`s on the seed's quiet Locations.
- The Activity Summary has no per-Location breakdown; per-Location verdicts appear only through the Location selector and the Attention List.
- Tolerance constants are tuned for this seed's volumes; they are in one settings dict for that reason.
