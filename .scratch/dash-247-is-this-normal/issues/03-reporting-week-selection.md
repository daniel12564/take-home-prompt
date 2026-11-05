# 03: Reporting Week selection and validation

**What to build:** The dashboard opens on the last complete Reporting Week before the Reference Date and lets the Customer Admin step to any earlier complete week; the in-progress week cannot be chosen. The Activity Summary endpoint accepts and validates `week_start` and `location`, resolving the week in the Account's own timezone, and rejects bad input with a field-level validation error. Metrics are not computed yet; the endpoint echoes the resolved week.

Spec: `.scratch/dash-247-is-this-normal/spec.md`. Decisions: `PLAN_REFINED.md` §3.2 (time), §3.9 (summary endpoint and errors). Glossary: Reporting Week, Reference Date.

**Blocked by:** 02 (Seeded Accounts and Locations with header selectors).

**Status:** ready-for-agent

- [ ] `DASHBOARD_REFERENCE_DATE` is a settings constant set to `2026-07-27`.
- [ ] A pure, database-free periods module computes: the Reporting Week (Monday 00:00 to next Monday 00:00 in a given IANA timezone, as UTC bounds) containing a date; the default week (last complete week before the Reference Date); the selectable range (first Monday on or after the data start, `2026-02-02`, through the default week); and whether a given `week_start` is valid.
- [ ] `GET /api/v1/accounts/{id}/dashboard/activity-summary/` accepts optional `week_start` (a Monday date) and `location`; the response contains `account_id`, `week_start`, `week_end` (the Sunday), the selected `location` or null, and an empty or placeholder `metrics` list. Omitted `week_start` resolves to the default week.
- [ ] `week_start` that is not a Monday, is before `2026-02-02`, or is not complete at the Reference Date (including `2026-07-27`) returns 400 `VALIDATION_ERROR` naming `week_start` in `errors`; a `location` the Account does not have returns 400 naming `location`; unknown Account returns 404.
- [ ] The header gains a week picker listing complete weeks newest first with human-readable labels; the selection is the `week` URL param (Monday date); the in-progress week is not offered; a missing or invalid `week` param falls back to the default week and normalises the URL.
- [ ] Changing the Account keeps the selected week.
- [ ] Pure-module tests cover week bounds for `America/Chicago`, `America/Phoenix` and `UTC`, a Sunday 23:30 local timestamp belonging to the earlier week, the default week, the range endpoints and each rejection reason.
- [ ] API tests cover default resolution when `week_start` is omitted, each 400 case with the field named, the foreign Location, and the 404.
