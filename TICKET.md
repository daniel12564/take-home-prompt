# Ticket

DASH-247 — Help customers understand whether their recent activity is normal

Customers looking at their dashboard can't tell whether this week's numbers are good, bad, or typical for them. Product wants the dashboard to help a customer answer "is this normal for us?" at a glance, without exporting data or calling their account manager.

Notes from product: probably involves comparing against some baseline, multi-location customers matter, a customer admin should be able to look at this Monday morning and act on it.

Out of scope per product: alerting/notifications, and predictive ML/forecasting. (An LLM used for explanation, summarization, or classification is not forecasting — that's fair game;)

## Explicitly out of scope

- **Auth / login** — assume a single trusted customer admin; a hardcoded identity is fine.
- **Alerting / notifications and predictive ML / forecasting** — per the ticket.
- **Production infra** — no Kubernetes or CI required. Local run is fine.
- **Visual polish** — function over form. Unstyled-but-clear beats pretty-but-broken.
