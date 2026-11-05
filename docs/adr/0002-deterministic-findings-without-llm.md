---
status: accepted
---

# Findings and their explanations are deterministic; no LLM in the dashboard

Every Finding is a structured object produced by fixed rules (Tolerance, no-activity, Account-wide rollup), and its explanation is rendered from that object by a template. We considered letting an LLM write the explanations, which the ticket explicitly allows, and rejected it for this version: it would put a network call, an API key and nondeterministic text on the hot path of a dashboard whose whole value is that a Customer Admin can trust the verdict at a glance, and it would make the explanation text untestable. The structured Finding is the contract; if an LLM is ever added it reads that object and rewrites the sentence, it never decides what is abnormal.

## Consequences

- Explanations are covered by golden-string unit tests.
- Any future LLM layer must be optional, fall back to the template, and receive Findings rather than raw Activity Events.
