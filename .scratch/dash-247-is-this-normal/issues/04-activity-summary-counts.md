# 04: Activity Summary counts for the selected week and scope

**What to build:** For the selected Account, Reporting Week and Location, the Activity Summary section shows how many calls were received, leads created and appointments set that week. Counts respect the Account's timezone week boundaries. Baseline and Status are not computed yet: every Metric shows as "insufficient data".

Spec: `.scratch/dash-247-is-this-normal/spec.md`. Decisions: `PLAN_REFINED.md` §3.3 (Metrics), §3.9 (summary payload), §3.10 (one grouped query). Glossary: Metric, Activity Summary.

**Blocked by:** 03 (Reporting Week selection and validation).

**Status:** resolved

- [x] A queryset method returns weekly counts grouped by Location, Event Type and week for an Account over a list of week starts, truncating weeks in the Account's timezone, optionally filtered to one Location. This is the only aggregation entry point; later tickets reuse it for the Baseline Window.
- [x] A dashboard service composes the periods module and the aggregation into the Activity Summary payload; the view only validates parameters, calls the service and wraps the result.
- [x] The `metrics` list has exactly three entries in a fixed order (`call_received`, `lead_created`, `appointment_set`), each with `current` (the week's count for the scope), and `baseline`, `delta`, `delta_pct` null with `status` `insufficient_data`; `baseline_weeks_used` is present and 0.
- [x] Account scope sums all Locations; Location scope counts only that Location; a week with no events yields zeros, not missing entries.
- [x] The Activity Summary section renders one card per Metric with its label and current count, a grey "insufficient data" badge, and loading, error and empty states; it refetches when Account, week or Location changes (query key by Account id, week and Location).
- [x] API tests over the fixture: Account scope totals and a single-Location scope for the default week; zeros for a Location with no events that week; an event at Sunday 23:30 `America/Chicago` counted in the earlier week; the endpoint runs within a fixed query budget independent of the number of Locations.
- [x] A component test renders the three Metric cards from a sample payload.

## Answer

Implemented on `dash-247-tickets-02-08` (aeee6b7). `make test-api` (52) and `make test-web` (39) pass; live counts for account 6 cross-checked against psql. Rendered cards not checked in a real browser.
