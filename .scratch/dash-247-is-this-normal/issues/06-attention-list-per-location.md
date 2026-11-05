# 06: Attention List with per-Location Findings

**What to build:** Below the Activity Summary, a Customer Admin with several Locations sees an Attention List for the selected week: one Finding per Location and Metric that deviated from its Baseline, a single "no activity" Finding for a Location that went silent, each marked critical or warning with a plain-language explanation, ordered so the most serious come first. When nothing deviated the section says so; when there is not enough history it explains why.

Spec: `.scratch/dash-247-is-this-normal/spec.md`. Decisions: `PLAN_REFINED.md` §3.6 (Findings 1–2, ordering, templates), §3.9 (`attention/`); ADR-0002. Glossary: Finding, Severity, No-activity Finding, Attention List.

**Blocked by:** 05 (Baseline and Status verdicts in the Activity Summary).

**Status:** resolved

- [x] A Finding is an immutable structured value with the shape agreed in the spec (scope, location, kind, event types, direction, severity, current, baseline, delta percentage, the Account-wide fields left null for now, and explanation). Explanations are rendered from the fields by one template per (kind, scope); nothing else produces explanation text.
- [x] The Location universe for a week is the set of Locations with any Activity Event in the Baseline Window or the viewed week.
- [x] A Location in the universe with zero Activity Events of any type in the viewed week yields exactly one `critical` No-activity Finding and no per-Metric Findings.
- [x] Every other (Location, Metric) whose Status is not `typical` yields one Finding with the Severity from ticket 05.
- [x] Ordering: `critical` before `warning`, then by absolute delta percentage descending; no cap.
- [x] `GET /api/v1/accounts/{id}/dashboard/attention/` accepts optional `week_start` with the same validation and errors as the summary endpoint and returns `week_start`, `week_end` and the ordered `findings`. An Account with insufficient history returns an empty list and a flag or reason the UI can show.
- [x] The endpoint reuses the weekly-counts aggregation for the window plus the viewed week in one grouped query and runs within a fixed query budget independent of Location count.
- [x] The Attention List section renders each Finding as a card: Location, Metric, direction wording (surges neutral, drops as drops), current vs typical, Severity styling; it has loading, error, "nothing needs attention this week" and "not enough history" states; it ignores the Location selector (always whole Account) and refetches on Account or week change.
- [x] Pure-module tests: the No-activity suppression; one golden string per template (per-Location metric above, below, zero, no activity); ordering.
- [x] API tests over the fixture: the default week yields exactly a `critical` No-activity Finding for South followed by a `warning` for North; Account B yields an empty list with the insufficient reason; validation errors match the summary endpoint; query budget.
- [x] Component tests: empty and insufficient states; a critical card renders before a warning card.

## Answer

Implemented on `dash-247-tickets-02-08` (e18ea1c). `make test-api` (134) and `make test-web` (67) pass; live results match PLAN_REFINED §3.13. Not checked in a browser. Deviation: PLAN §3.12 says North has 12 calls vs baseline 5, but the §3.6 severity rule (|delta| >= 2 x tolerance) makes that `critical`, not the `warning` the ticket requires. The fixture now uses 11 calls (deviation 6, `warning`). Plan and fixture should be reconciled.
