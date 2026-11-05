# 07: Account-wide Findings

**What to build:** When most of an Account's Locations move in the same direction on the same Metric in the same week, the Attention List shows one Account-wide Finding at the top ("Calls were far above typical at 15 of 15 locations…") instead of a card per Location, naming the day if the week's activity was concentrated on one. Locations that moved the other way are still listed individually. Accounts with one or two Locations never roll up.

Spec: `.scratch/dash-247-is-this-normal/spec.md`. Decisions: `PLAN_REFINED.md` §3.6 (Findings 3–4, merge, one-day callout). Glossary: Account-wide Finding.

**Blocked by:** 06 (Attention List with per-Location Findings).

**Status:** resolved

- [x] `DASHBOARD_RULES` gains `rollup_min_locations` 3, `rollup_min_share` 0.5 and `one_day_concentration_share` 0.6.
- [x] For each (Metric, direction), when at least 3 Locations and at least half of the Location universe have that Status, one Account-wide Finding replaces those per-Location Findings; per-Location Findings in the opposite direction, and No-activity Findings, are kept.
- [x] Accounts whose universe has fewer than 3 Locations never produce Account-wide Findings.
- [x] Account-wide Findings in the same direction across several Metrics merge into one Finding listing all affected Metrics, with per-Metric affected counts available in the payload.
- [x] Only for an Account-wide Finding, a single additional daily-grouped query for the viewed week determines whether more than 60 % of a Metric's events fell on one local day; if so the day is named in the explanation and returned as `concentrated_on`.
- [x] Account-wide Findings sort before all per-Location Findings; `affected_locations` and `total_locations` are populated.
- [x] The Attention List renders an Account-wide Finding as a visually distinct full-width card at the top, with the "N of M locations" count and the day callout when present.
- [x] Pure-module tests: 3 of 5 fires, 2 of 5 does not, 3 of 10 does not, 1- and 2-Location universes never roll up, opposite-direction survivors, multi-Metric merge, golden strings for the Account-wide template with and without the day callout.
- [x] API tests over the fixture: week 6 (all three Locations at 4× calls) yields exactly one Account-wide Finding for calls `above` and no per-Location call Findings; the default week is unchanged from ticket 06; query budget allows exactly one extra query only when an Account-wide Finding exists.
- [x] Component test: an Account-wide card renders above per-Location cards.

## Answer

Implemented on `dash-247-tickets-02-08` (5c08578). `make test-api` (162) and `make test-web` (72) pass; account 6 week 2026-06-01 collapses to one Account-wide Finding (15/15/14 of 15, concentrated on 2026-06-03). Not checked in a browser. Deviations: added `affected_by_metric` to the Finding payload; Account-wide `baseline` is the sum of affected Locations baselines (37.5), not the Account total (40.5). For ticket 08: the live API shows extra per-Location warnings for account 6 on 2026-06-29 and 2026-04-13 beyond the §3.13 checklist.
