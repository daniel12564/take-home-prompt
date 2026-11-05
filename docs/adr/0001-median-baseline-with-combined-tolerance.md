---
status: accepted
---

# Baseline is a median over trailing complete weeks, judged with a combined tolerance

A Metric's Baseline is the median of the 8 complete Reporting Weeks preceding the viewed one (minimum 4), and its Status leaves `typical` only when the deviation exceeds `max(3, 0.30 × baseline, 1.5 × √baseline)`. We chose this over a mean with a percentage threshold because per-Location weekly counts in this domain are tiny (typically 1–5) and the data contains single-day spikes an order of magnitude above normal: a mean is poisoned for the whole window after such a spike, and a percentage threshold alone flags 3→1 swings that are pure noise. The median ignores one outlier week outright; the absolute floor and square-root term stop small counts from producing verdicts; the relative term still scales for high-volume Accounts.

## Considered options

- Mean ± k·stddev (z-score): 8 data points give an unstable stddev, and one spike inflates it enough to hide every later deviation.
- Percentage change only: meaningless below ~10 events per week, which is most Locations.
- Same-weekday or seasonal adjustment: forecasting-adjacent, out of scope, and unneeded for the question "is this week typical for us".

## Consequences

- The first 4 weeks of an Account's history show `insufficient_data` instead of a verdict.
- The five constants are tuned for the seeded volumes and live together in `DASHBOARD_RULES`; retuning them is expected if real volumes differ.
