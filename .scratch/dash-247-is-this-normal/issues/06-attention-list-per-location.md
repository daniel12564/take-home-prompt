# 06: Attention List with per-Location Findings

**What to build:** Below the Activity Summary, a Customer Admin with several Locations sees an Attention List for the selected week: one Finding per Location and Metric that deviated from its Baseline, a single "no activity" Finding for a Location that went silent, each marked critical or warning with a plain-language explanation, ordered so the most serious come first. When nothing deviated the section says so; when there is not enough history it explains why.

Spec: `.scratch/dash-247-is-this-normal/spec.md`. Decisions: `PLAN_REFINED.md` §3.6 (Findings 1–2, ordering, templates), §3.9 (`attention/`); ADR-0002. Glossary: Finding, Severity, No-activity Finding, Attention List.

**Blocked by:** 05 (Baseline and Status verdicts in the Activity Summary).

**Status:** ready-for-agent

- [ ] A Finding is an immutable structured value with the shape agreed in the spec (scope, location, kind, event types, direction, severity, current, baseline, delta percentage, the Account-wide fields left null for now, and explanation). Explanations are rendered from the fields by one template per (kind, scope); nothing else produces explanation text.
- [ ] The Location universe for a week is the set of Locations with any Activity Event in the Baseline Window or the viewed week.
- [ ] A Location in the universe with zero Activity Events of any type in the viewed week yields exactly one `critical` No-activity Finding and no per-Metric Findings.
- [ ] Every other (Location, Metric) whose Status is not `typical` yields one Finding with the Severity from ticket 05.
- [ ] Ordering: `critical` before `warning`, then by absolute delta percentage descending; no cap.
- [ ] `GET /api/v1/accounts/{id}/dashboard/attention/` accepts optional `week_start` with the same validation and errors as the summary endpoint and returns `week_start`, `week_end` and the ordered `findings`. An Account with insufficient history returns an empty list and a flag or reason the UI can show.
- [ ] The endpoint reuses the weekly-counts aggregation for the window plus the viewed week in one grouped query and runs within a fixed query budget independent of Location count.
- [ ] The Attention List section renders each Finding as a card: Location, Metric, direction wording (surges neutral, drops as drops), current vs typical, Severity styling; it has loading, error, "nothing needs attention this week" and "not enough history" states; it ignores the Location selector (always whole Account) and refetches on Account or week change.
- [ ] Pure-module tests: the No-activity suppression; one golden string per template (per-Location metric above, below, zero, no activity); ordering.
- [ ] API tests over the fixture: the default week yields exactly a `critical` No-activity Finding for South followed by a `warning` for North; Account B yields an empty list with the insufficient reason; validation errors match the summary endpoint; query budget.
- [ ] Component tests: empty and insufficient states; a critical card renders before a warning card.
