# DASH-247 — Help customers understand whether their recent activity is normal

Status: ready-for-agent

Source: `TICKET.md`, `PROJECT_BACKGROUND.md`, `PLAN_REFINED.md` (decisions), `GLOSSARY.md` (vocabulary), ADR-0001 and ADR-0002.

## Problem Statement

A Customer Admin opens the Relay reporting dashboard and sees raw totals per Location. They cannot tell whether this week's numbers are good, bad, or typical for their business, so they export data or call their account manager to ask "is this normal for us?". Customer Admins with many Locations have a second problem: even when something is off, nothing on the dashboard tells them which Location it is or what is unusual about it. The dashboard should let a Customer Admin answer both questions on a Monday morning, at a glance, and act on them.

## Solution

A single-page reporting dashboard with two sections and three selectors.

The **Activity Summary** shows, for the selected Reporting Week, the three activity Metrics (calls received, leads created, appointments set) for the whole Account or one Location. Each Metric shows the week's count, its Baseline (what is typical for this Account or Location), and a colour-coded Status: typical, above, below, or insufficient data.

The **Attention List** lists the Findings for that Reporting Week: Locations whose activity deviated from their Baseline, Locations that went silent, and, when most Locations move together, a single Account-wide Finding instead of a wall of identical cards. Each Finding carries a plain-language explanation of what was observed and what is typical.

The selectors are Account (which customer is being viewed, since there is no login), Reporting Week (any complete Monday–Sunday week in the data), and Location (whole Account or one site). All three are reflected in the page URL so a view can be bookmarked or shared.

Verdicts are deterministic. "Typical" is the median of the trailing eight complete weeks; a Metric is flagged only when it moves beyond a Tolerance that combines a relative and an absolute allowance, so small weekly counts do not generate noise. There is no LLM, no alerting, and no forecasting.

## User Stories

Viewing the summary

1. As a Customer Admin, I want to see this week's count of calls received, leads created and appointments set for my whole Account, so that I know what happened without adding up Locations.
2. As a Customer Admin, I want each Metric to show the value that is typical for my Account next to this week's count, so that I have a concrete reference instead of a feeling.
3. As a Customer Admin, I want each Metric to be colour-coded as typical, above or below, so that I can judge the week at a glance without reading numbers.
4. As a Customer Admin, I want to see the difference from typical as both a number and a percentage, so that I understand the size of the deviation.
5. As a Customer Admin, I want "above typical" to be visually distinct from "below typical" and from "typical", so that I do not mistake a surge for a drop.
6. As a Customer Admin, I want a Metric whose history is too short to judge to say "insufficient data" rather than show a misleading verdict, so that I trust the verdicts that are shown.
7. As a Customer Admin, I want to know how many weeks of history the Baseline was computed from, so that I can weigh how much to trust it.
8. As a Customer Admin whose Account has no activity at all, I want the dashboard to say so clearly instead of showing zeros marked as typical, so that I do not think everything is fine.

Choosing what to look at

9. As a Customer Admin, I want the dashboard to open on the last complete week, so that on Monday morning I am looking at the week that just ended.
10. As a Customer Admin, I want to pick any earlier complete week, so that I can review how a past week compared to what was typical at that time.
11. As a Customer Admin, I want the current in-progress week to be unavailable in the week picker, so that I am never shown a half-week judged against full weeks.
12. As a Customer Admin, I want weeks to run Monday to Sunday in my business's own timezone, so that a Sunday-night call is counted in the week I think it belongs to.
13. As a Customer Admin, I want to narrow the Activity Summary to a single Location, so that I can check whether one site is typical for itself.
14. As a Customer Admin, I want the Location selector to list every Location my Account has ever had activity at, sorted by name, so that I can find a site quickly.
15. As a Customer Admin, I want the Location selector to reset when I change Account, so that I am never shown a Location that belongs to another Account.
16. As a Customer Admin, I want the selected Account, week and Location to be in the page URL, so that I can bookmark a view or send it to a colleague.
17. As a Customer Admin, I want to switch between Accounts from the header, so that, in the absence of a login, I can view any customer's dashboard.
18. As a Customer Admin, I want the Account selector to show each Account's name and how many Locations it has, so that I can pick the one I mean.

Finding the Locations that need attention

19. As a Customer Admin with many Locations, I want a list of only the Locations whose activity deviated from their own typical, so that I do not have to scan every site.
20. As a Customer Admin, I want each Finding to say which Location, which Metric, which direction, this week's value and the typical value, so that I understand what was flagged and why.
21. As a Customer Admin, I want each Finding to have a one- or two-sentence plain-language explanation, so that I can read it without interpreting numbers.
22. As a Customer Admin, I want Findings to be marked critical or warning, so that I know which to look at first.
23. As a Customer Admin, I want a Location that dropped to zero on a Metric it normally has to be marked critical, so that a site that stopped answering the phone stands out.
24. As a Customer Admin, I want a Location that recorded no activity of any kind to appear as a single "no activity" Finding rather than three separate drops, so that the list stays readable.
25. As a Customer Admin, I want critical Findings listed before warnings and larger deviations before smaller ones, so that the top of the list is where I should start.
26. As a Customer Admin, I want surges above typical to appear in the Attention List too, phrased neutrally rather than as problems, so that I notice an unusual spike (which may be a data issue) without being told something is wrong.
27. As a Customer Admin whose Locations all moved in the same direction in the same week, I want one Account-wide Finding that says how many Locations were affected, so that I see one thing happened to the whole business rather than fifteen cards saying the same thing.
28. As a Customer Admin reading an Account-wide Finding, I want it to tell me when most of that week's activity landed on a single day, so that I can connect the spike to an event on that day.
29. As a Customer Admin, I want a Location that moved against the Account-wide trend to still be listed individually, so that the rollup does not hide a site behaving differently.
30. As a Customer Admin with one or two Locations, I want Findings always listed per Location, so that a rollup never hides which site is meant.
31. As a Customer Admin, I want the Attention List to say explicitly when there is nothing to report for the week, so that an empty list reads as good news rather than as a loading error.
32. As a Customer Admin, I want the Attention List to explain when there is not enough history to produce Findings, so that I know why it is empty.

Trusting the verdicts

33. As a Customer Admin with low weekly volumes, I want small swings (for example three calls one week and one the next) not to be flagged, so that the dashboard does not cry wolf.
34. As a Customer Admin, I want one freak week in the past not to change what the dashboard considers typical for the following two months, so that a one-off spike does not hide real changes afterwards.
35. As a Customer Admin, I want the same week to produce the same verdicts every time I load it, so that I can discuss it with a colleague looking at the same page.
36. As a Customer Admin, I want an Account-level Status to be computed from the Account's own weekly totals, not from adding up per-Location verdicts, so that the whole-Account view is meaningful on its own.

Robustness

37. As a Customer Admin, I want a clear loading state while data is fetched, so that I know the page is working.
38. As a Customer Admin, I want a readable error message if the data cannot be loaded, so that I know to retry rather than assume there was no activity.
39. As a Customer Admin, I want an invalid week in the URL (not a Monday, too early, or not yet complete) to be rejected with an explanation, so that a mistyped link does not silently show something else.
40. As a Customer Admin, I want an unknown Account or Location in the URL to produce a clear not-found or validation message, so that I can correct it.

Operating the application

41. As a developer, I want to start the database, API and web app with one command, so that the project runs locally without manual setup.
42. As a developer, I want one command that migrates the database and loads the seed data, so that a fresh checkout reaches a demo-ready state.
43. As a developer, I want the seed load to be idempotent with an explicit flush option, so that re-running setup is safe and reloading is deliberate.
44. As a developer, I want the seed to preserve the original record ids, so that tests and discussions can cite specific events.
45. As a developer, I want separate commands to run the backend and frontend test suites, so that I can iterate on one side quickly.
46. As a developer, I want every rule constant (baseline length, tolerances, rollup thresholds) in one settings dictionary, so that retuning for real volumes is a one-place change.
47. As a developer, I want the normality rules implemented as pure functions with no database access, so that they can be tested exhaustively and reused unchanged by any future consumer.
48. As a developer, I want the Finding to be a structured object from which explanations are rendered, so that any future presentation layer (including an optional LLM rewrite) consumes facts rather than inventing them.
49. As a developer, I want all API responses in a single success/error envelope with machine-readable error codes, so that the frontend handles errors uniformly.
50. As a developer, I want the dashboard endpoints to run a bounded number of database queries regardless of Location count, so that a 15-Location Account is as fast as a single-site one.

## Implementation Decisions

Vocabulary: all terms below are as defined in `GLOSSARY.md` (Account, Customer Admin, Location, Activity Event, Event Type, Metric, Reporting Week, Reference Date, Baseline, Baseline Window, Status, Tolerance, Finding, Severity, No-activity Finding, Account-wide Finding, Attention List, Activity Summary).

Scope and identity

- No authentication. The Account being viewed is chosen from a header selector and travels in the API path on every request.
- Nothing is written by the application at runtime; all endpoints are read-only.

Time

- The Reference Date is a fixed settings constant (`2026-07-27`, the last day in the seed). It determines the default Reporting Week and which weeks are complete.
- A Reporting Week runs Monday 00:00 to the next Monday 00:00 in the Account's IANA timezone and is converted to UTC for querying. Weeks are never cut on UTC boundaries.
- The default Reporting Week is the last complete week before the Reference Date. The week picker offers every complete week from the first Monday in the data onward; the in-progress week is not selectable and is rejected by the API.

Metrics, Baseline, Status

- Three Metrics: counts of `call_received`, `lead_created`, `appointment_set` Activity Events. Outcome- and duration-derived Metrics are stored but not computed (ticket scope; the seed has no outcome anomalies).
- Baseline Window: the 8 complete Reporting Weeks immediately before the viewed week, clipped at the start of the data. Fewer than 4 weeks → `insufficient_data`. An Account with no Activity Events in the window or the viewed week → `insufficient_data` for every Metric.
- Baseline: median of the Metric over the window. For Account scope, the median of weekly sums (ADR-0001).
- Tolerance and Severity constants, in one settings dictionary (values from the simulation against the seed):

  ```
  baseline_weeks 8, min_baseline_weeks 4
  tolerance = max(3, 0.30 * baseline, 1.5 * sqrt(baseline))
  critical when |current - baseline| >= 2 * tolerance, or current == 0 with baseline >= 3
  rollup when >= 3 locations and >= 50% of the location universe share (metric, direction)
  one-day concentration callout when > 60% of a metric's weekly events fall on one local day
  ```

- Status: `typical` when the deviation is below Tolerance; otherwise `above` or `below`. Baseline 0 with current 0 is `typical`; Baseline 0 with current at or above the absolute floor is `above`.
- Colour mapping: `typical` green, `below` red, `above` amber, `insufficient_data` grey.

Findings

- Location universe for a week: Locations with any Activity Event in the Baseline Window or the viewed week. The Location selector lists all-time distinct Locations.
- No-activity Finding: a Location in the universe with zero Activity Events in the viewed week yields one `critical` Finding and no per-Metric Findings.
- Per-Location Finding: one per (Location, Metric) whose Status is not `typical`.
- Account-wide Finding: per (Metric, direction), when the rollup thresholds are met, replaces the matching per-Location Findings; Locations deviating the other way remain. Accounts with fewer than 3 Locations never roll up. Account-wide Findings in the same direction across several Metrics merge into one.
- One-day concentration is computed only for Account-wide Findings, with a single additional daily-grouped query.
- Finding shape (from the simulation; this is the contract between rules, API, UI and tests):

  ```
  scope: account | location
  location: name or null
  kind: metric | no_activity
  event_types: one Event Type, or several for a merged Account-wide Finding
  direction: above | below
  severity: warning | critical
  current, baseline, delta_pct
  affected_locations, total_locations, concentrated_on   (Account-wide only)
  explanation: text rendered from the fields above
  ```

- Explanation text is produced by one template per (kind, scope) from the Finding fields and never the other way round (ADR-0002). No LLM.
- Ordering: Account-wide first, then `critical`, then `warning`; within a tier by absolute percentage deviation, descending. No cap.

Data model and seed

- Two models mapped onto the seed's table names: Account (name, industry, IANA timezone, created_at) and Activity Event (account, location as free text, event type, UTC timestamp, optional duration, optional outcome). Event type and outcome are constrained by choices. No Location table.
- Indexes on (account, occurred_at) and (account, location, event type, occurred_at).
- Seed pipeline: a committed one-off converter turns the provided SQL seed into two CSV files (empty cell = NULL), also committed. A management command loads the CSVs with batched bulk creation inside a transaction, preserves ids, resets the sequences, skips when Accounts already exist, and reloads on an explicit flush flag.

API

- Base path `/api/v1/`, Account id in the path:
  - list Accounts (id, name, timezone, location count)
  - list an Account's Locations (sorted names)
  - Activity Summary for an Account, optional `week_start` (a Monday; default when omitted) and optional `location`
  - Attention List for an Account, optional `week_start`
- Activity Summary returns the Account id, week start and end, the selected Location or null, the number of Baseline weeks used, and one entry per Metric with current, baseline, delta, delta percentage and Status. No per-Location breakdown; the Attention List covers that.
- Attention List returns week start and end and the ordered list of Findings.
- Every response uses one envelope: success with a `data` member, or failure with `message`, per-field `errors` and an `error_code`. Unknown Account → 404 `NOT_FOUND`. Invalid, too-early or incomplete `week_start`, or a Location not belonging to the Account → 400 `VALIDATION_ERROR` naming the field.

Backend architecture

- Django apps for accounts and activity; API views under a versioned API package; shared envelope and exception handling in a core package, following the repo's backend rules.
- The normality logic is a set of pure modules (periods, baseline, rules, findings, explanations) operating on plain data. One service entry point performs the aggregation query (weekly counts grouped by Location and Event Type, truncated to weeks in the Account's timezone) and feeds the pure modules. Views only validate parameters, call the service, and wrap the result.
- Aggregation is one grouped query per endpoint call (plus the optional daily query for Account-wide Findings); per-Location work never issues per-Location queries.

Frontend architecture

- Vite, React, TypeScript, TanStack Query, Tailwind. No router library, global store, form library or component kit: one page, three selectors, two sections.
- Selector state lives in URL search params (account, week, location). Changing the Account clears the Location and keeps the week.
- Query keys are hierarchical per Account, week and Location so a selector change refetches only what depends on it.
- Every data region has loading, error, empty and insufficient-data states.

Tooling

- Docker Compose with database, API and web services. A Makefile provides: start services, stop and wipe, migrate-and-seed, backend tests, frontend tests. Python dependencies via `uv`, Node via `npm`.

## Testing Decisions

What makes a good test here: assert on observable behaviour (HTTP responses, rendered states, returned Statuses and Findings), never on how the median or Tolerance is computed internally. Tests use hand-built inputs with known answers; they do not load the full seed. Three seams, agreed with the user, from highest to lowest:

1. **HTTP API** (primary). DRF test client against the four endpoints, over one handcrafted fixture built by a factory in the test configuration: Account A in `America/Chicago` with Locations North, South and East; Account B in `UTC` with no Activity Events; ten Reporting Weeks ending at the default week with steady volumes (about 5 calls, 2 leads, 1 appointment per Location per week); planted signals: South has no events in the default week, North has 12 calls in the default week, all three Locations have 4× calls in week 6. Assertions: Account list with Location counts; Location list sorted and 404 on unknown Account; Summary default week when `week_start` omitted; North calls `above`; Account totals from weekly sums; Baseline weeks used; Account B `insufficient_data` throughout; 400 with the field named for too-early, non-Monday and incomplete weeks and for a foreign Location; Attention default week is exactly a `critical` No-activity Finding for South then a `warning` for North; week 6 is one Account-wide Finding with no per-Location Findings and later weeks' Baselines unaffected by it; Account B empty list; envelopes on success and failure; a Sunday 23:30 Chicago event counted in the earlier week; a fixed query budget per dashboard endpoint.
2. **Pure services** (secondary), no database. Only the cases cheaper to enumerate than to drive over HTTP: the Tolerance table at Baselines 0, 1, 3, 4, 10 and 40; 3→1 not flagged; 5→0 critical; 0→3 above warning; median unmoved by one 10× week; window clipping and the minimum-weeks rule; week boundaries in three timezones; rollup at 3 of 5 fires, 2 of 5 does not, single-Location never; opposite-direction survivors; multi-Metric merge; ordering; one golden string per explanation template including the one-day callout.
3. **React components** (tertiary), Vitest and Testing Library: Status badge colour mapping; Activity Summary and Attention List empty, insufficient-data and error states.

Prior art: none, the repository is empty. The backend follows `pytest` + `pytest-django` conventions with fixtures in the test configuration module; the frontend follows Vitest + Testing Library conventions from the Vite template.

Not tested automatically: the full seed. The expected verdicts for the seeded signals (account 6 week of 2026-06-01 collapsing to one Account-wide Finding concentrated on 2026-06-03; account 15 Site B calls 0 vs 5 critical in the default week; account 20 insufficient everywhere; account 16 all typical) are a manual acceptance checklist in `PLAN_REFINED.md`.

## Out of Scope

- Authentication, authorisation, multi-user concerns.
- Alerting, notifications, scheduled checks.
- Predictive ML or forecasting; seasonal or weekday-adjusted Baselines.
- Any LLM usage (ADR-0002).
- Metrics derived from Outcome or duration (missed-call rate, no-show rate, conversion, call length).
- Arbitrary date ranges, partial weeks, daily or monthly views.
- A Location entity with its own attributes.
- Writes of any kind (annotations, acknowledgements, dismissals).
- Production infrastructure, CI, deployment, visual polish beyond clear and functional.
- End-to-end browser tests and tests against the full seed.

## Further Notes

- The seed's Account 6 (15 Locations) exercises every path: the one-day spike, dark weeks for Site G and Site N, and ordinary weeks. Accounts 8, 13, 16 and 19 are single-Location; Account 20 has no data. Weeks before 2026-03-02 show `insufficient_data` by construction.
- Replacing the fixed Reference Date with the real date is a one-line change, but with this seed it would produce an empty dashboard; the constant is deliberate.
- The Tolerance constants are tuned for the seed's volumes (median 3–5 calls per Location per week). They are centralised so a real deployment can retune them without touching the rules.
- If an LLM layer is ever added, it must be optional, fall back to the template text, and receive Findings rather than raw Activity Events (ADR-0002).
