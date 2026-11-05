# 02: Seeded Accounts and Locations with header selectors

**What to build:** After `make setup`, a Customer Admin opens the dashboard, picks any of the 20 seeded Accounts from a header selector (showing name and Location count), then picks one of that Account's Locations or "All locations"; both choices are reflected in the URL and survive a reload. Changing the Account clears the Location.

Spec: `.scratch/dash-247-is-this-normal/spec.md`. Decisions: `PLAN_REFINED.md` §3.7 (data model), §3.8 (seed), §3.9 (`accounts/`, `accounts/{id}/locations/`), §3.12 (fixture).

**Blocked by:** 01 (Runnable skeleton).

**Status:** resolved

- [x] Account model (name, industry, IANA timezone, created_at) and Activity Event model (account, free-text location, event type, UTC timestamp, optional duration, optional outcome) map onto the seed's table names; event type and outcome are constrained by choices; indexes on (account, occurred_at) and (account, location, event type, occurred_at). No Location table.
- [x] A committed one-off converter turns the provided SQL seed (moved under the backend seed directory) into `accounts.csv` and `activity_events.csv`; empty cells mean NULL; both CSVs are committed.
- [x] `seed_activity` loads the CSVs with batched bulk creation inside one transaction, preserves the original ids, resets both sequences, skips when Accounts already exist, and reloads with `--flush`. `make setup` ends with 20 Accounts and 12,626 Activity Events; running it twice does not duplicate.
- [x] Both models are registered in the Django admin.
- [x] `GET /api/v1/accounts/` returns id, name, timezone and `location_count` (all-time distinct Locations) for every Account, including Account 20 with 0.
- [x] `GET /api/v1/accounts/{id}/locations/` returns the Account's all-time distinct Location names sorted; unknown Account returns 404 `NOT_FOUND` in the envelope.
- [x] The header shows an Account selector and a Location selector; selection is stored in URL search params (`account`, `location`); changing the Account removes `location`; the Location selector is disabled with an explanatory label when the Account has no Locations.
- [x] TanStack Query keys are hierarchical (`accounts`, then `locations` by Account id).
- [x] The handcrafted test fixture factory from the spec is introduced: Account A (`America/Chicago`, Locations North/South/East, ten Reporting Weeks of steady volume with the three planted signals) and Account B (`UTC`, no events). Later tickets extend assertions, not the fixture.
- [x] API tests cover both endpoints over the fixture, including Location counts of 3 and 0 and the 404.
- [x] A component test covers the Account-change-clears-Location behaviour.

## Answer

Implemented on `dash-247-tickets-02-08`. `make test-api` (15) and `make test-web` (12) pass; seed loaded and verified via `make setup`. Browser click-through not verified.
