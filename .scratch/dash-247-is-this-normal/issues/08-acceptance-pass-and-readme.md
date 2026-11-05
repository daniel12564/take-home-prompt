# 08: Seed acceptance pass and README

**What to build:** A reviewer can clone the repo, follow the README, and within a few minutes see the dashboard reproduce every expected verdict from the real seed: the account 6 one-day spike collapsing into a single Account-wide Finding, Site B of account 15 going to zero calls, the no-data Account, the single-site Account with nothing to report, and the early weeks with insufficient history. Any discrepancy between the running app and the agreed expectations is fixed in this ticket.

Spec: `.scratch/dash-247-is-this-normal/spec.md`. Decisions: `PLAN_REFINED.md` §3.13 (manual acceptance checklist), §5 (known limitations); ADR-0001, ADR-0002.

**Blocked by:** 07 (Account-wide Findings).

**Status:** ready-for-agent

- [ ] From a clean checkout, `make up` then `make setup` reaches a usable dashboard with no manual steps beyond copying `.env.example`.
- [ ] Every row of the manual acceptance checklist in `PLAN_REFINED.md` §3.13 is verified against the running app (summary values, Statuses, Findings, Severities, Account-wide collapse with the 2026-06-03 callout, validation and not-found errors). Discrepancies are either fixed or, if the agreed expectation was wrong, corrected in `PLAN_REFINED.md` with a note explaining why.
- [ ] `make test-api` and `make test-web` are green.
- [ ] README at the repo root covers: what the dashboard answers and for whom; the `make` workflow; how to pick Accounts/weeks/Locations and what the colours and Severities mean; the fixed Reference Date and why; where the rule constants live; a pointer to `GLOSSARY.md`, `docs/adr/`, `PLAN_REFINED.md` and the spec; known limitations (no auth, no LLM, counts only, unit and fixture-level API tests only, constants tuned to the seed).
- [ ] The repo root contains no leftover scratch artefacts from implementation; `PLAN.md` remains untouched.
