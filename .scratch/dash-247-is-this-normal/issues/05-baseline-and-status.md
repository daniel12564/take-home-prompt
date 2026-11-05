# 05: Baseline and Status verdicts in the Activity Summary

**What to build:** Each Metric in the Activity Summary now shows what is typical for the selected scope (the Baseline), the difference from it, and a colour-coded Status: typical (green), above (amber), below (red) or insufficient data (grey). Small weekly counts do not produce verdicts from noise; one freak week in the past does not move the Baseline; an Account with no history says so.

Spec: `.scratch/dash-247-is-this-normal/spec.md`. Decisions: `PLAN_REFINED.md` §3.4 (Baseline), §3.5 (Status and Tolerance); ADR-0001. Glossary: Baseline, Baseline Window, Tolerance, Status.

**Blocked by:** 04 (Activity Summary counts for the selected week and scope).

**Status:** resolved

- [x] All rule constants live in one `DASHBOARD_RULES` settings dictionary: `baseline_weeks` 8, `min_baseline_weeks` 4, `tolerance_abs_min` 3, `tolerance_rel` 0.30, `tolerance_sqrt_factor` 1.5, `critical_tolerance_multiple` 2, plus the rollup and one-day keys reserved for ticket 07. No rule constant appears anywhere else.
- [x] A pure baseline module computes the Baseline Window (the 8 complete weeks before the viewed week, clipped at `2026-02-02`) and the Baseline as the median of a Metric's weekly values; Account scope uses the median of weekly sums.
- [x] A pure rules module returns a Status for (current, baseline): `tolerance = max(3, 0.30 × baseline, 1.5 × √baseline)`; deviation below Tolerance is `typical`, otherwise `above` or `below`; baseline 0 with current 0 is `typical`; fewer than 4 weeks in the window is `insufficient_data`. It also returns Severity (`critical` at twice the Tolerance or current 0 with baseline ≥ 3, else `warning`) for use by ticket 06.
- [x] An Account with no Activity Events in the window or the viewed week is `insufficient_data` for every Metric regardless of the zero Baseline.
- [x] The summary payload fills `baseline`, `delta`, `delta_pct` (one decimal), `status` and `baseline_weeks_used` (actual number of weeks in the window).
- [x] The Activity Summary cards show Baseline and delta and a Status badge with the agreed colours; `above` is not phrased as a problem; `insufficient_data` cards explain that more weeks of history are needed.
- [x] Pure-module tests: Tolerance table at Baselines 0, 1, 3, 4, 10 and 40; 3→1 is `typical`; 5→0 is `below` and `critical`; 0→3 is `above` and `warning`; the median is unmoved by a single 10× week; window clipping at the data start; the minimum-weeks rule; Account sums.
- [x] API tests over the fixture: North calls `above` in the default week; Account totals derive from weekly sums; `baseline_weeks_used` is 8 for the default week and smaller for the second week of data; Account B is `insufficient_data` on every Metric; the week-6 spike does not change later weeks' Baselines.
- [x] Component tests: the badge renders the agreed colour for each of the four Statuses and the insufficient-data explanation.

## Answer

Implemented on `dash-247-tickets-02-08` (0f81fca). `make test-api` (104) and `make test-web` (51) pass; verdicts checked against PLAN_REFINED §3.13 via curl on the real seed. Not checked in a browser. Known gap for ticket 08: the card text for insufficient data is the same for short history and for an Account with no activity (spec story 8).
