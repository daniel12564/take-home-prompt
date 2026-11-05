# Relay Reporting Dashboard

Relay tracks inbound customer activity (calls, leads, appointments) for service businesses across their locations. This context is the reporting dashboard that tells a customer whether a week's activity is typical for them and which locations need attention.

## Language

### Who and where

**Account**:
A Relay customer: the business whose activity is being reported. Owns one or more Locations and has a single IANA timezone used for all its reporting.
_Avoid_: Customer, client, tenant, organisation

**Customer Admin**:
The person at an Account who looks at the dashboard. In this version there is exactly one, trusted, and unauthenticated.
_Avoid_: User, viewer

**Location**:
A physical site or branch of an Account where inbound activity is attributed. Identified by its name within the Account; it has no attributes of its own.
_Avoid_: Site, branch, store, office

### What happened

**Activity Event**:
A single inbound occurrence at a Location: a call received, a lead created, or an appointment set. Has a UTC timestamp, and may carry a duration (calls) and an outcome.
_Avoid_: Activity, event, inbound event, interaction

**Event Type**:
The kind of Activity Event: `call_received`, `lead_created`, or `appointment_set`.
_Avoid_: Activity type, category, channel

**Outcome**:
What became of an Activity Event (for calls: connected, missed, voicemail; for leads: open, converted; for appointments: completed, no-show). Stored but not used for any verdict in this version.
_Avoid_: Status, result, disposition

**Metric**:
A number computed from Activity Events for a scope and a Reporting Week. In this version the only Metrics are the three Event Type counts.
_Avoid_: KPI, stat, measure

### When

**Reporting Week**:
The Monday-to-Sunday period being viewed, with boundaries at midnight in the Account's timezone. The default Reporting Week is the last complete one before the Reference Date.
_Avoid_: Current week, this week, period, date range

**Reference Date**:
The fixed date the dashboard treats as "today". Determines which Reporting Week is the default and which weeks are complete.
_Avoid_: Now, today, as-of date

**Baseline**:
The typical value of a Metric for a scope: the median of that Metric over the complete Reporting Weeks immediately preceding the viewed one (the Baseline Window).
_Avoid_: Historical, average, normal numbers, typical numbers, expected

**Baseline Window**:
The trailing complete Reporting Weeks used to compute a Baseline. Has a target length and a minimum length below which no verdict is given.
_Avoid_: Lookback, history, training period

### Verdicts

**Status**:
The verdict on one Metric for one scope and Reporting Week, compared to its Baseline: `typical`, `above`, `below`, or `insufficient_data`.
_Avoid_: Health, state, normality, flag, color

**Tolerance**:
How far a Metric may deviate from its Baseline before its Status stops being `typical`. Combines a relative and an absolute allowance so that small counts do not produce verdicts from noise.
_Avoid_: Threshold, sensitivity, band

**Finding**:
One detected deviation worth a Customer Admin's attention: a scope (an Account or a Location), a Metric, a direction, the observed and Baseline values, a Severity, and a plain-language explanation derived from those facts.
_Avoid_: Anomaly, issue, alert, notification, incident, problem

**Severity**:
How serious a Finding is: `warning` or `critical`.
_Avoid_: Priority, level, urgency

**No-activity Finding**:
A single Finding for a Location that was active during the Baseline Window but recorded no Activity Events at all in the viewed Reporting Week. Replaces the per-Metric Findings that Location would otherwise produce.
_Avoid_: Dark location, silent location, outage

**Account-wide Finding**:
A single Finding that replaces many per-Location Findings when most Locations of an Account deviate in the same direction on the same Metric in the same Reporting Week.
_Avoid_: Rollup, aggregate finding, global anomaly

**Attention List**:
The dashboard section listing the Findings for the viewed Reporting Week, Account-wide Findings first, then per-Location Findings ordered by Severity.
_Avoid_: Alerts, issues list, problems, anomalies panel

**Activity Summary**:
The dashboard section showing each Metric for the viewed Reporting Week, its Baseline and its Status, for the whole Account or a selected Location.
_Avoid_: Resume, overview, scorecard, KPIs
