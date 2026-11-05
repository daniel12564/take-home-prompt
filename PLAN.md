# Plan

To keep it simple, the idea for the dashboard shold be just a single page with something like:
- a section to display a resume of how the distinct activities (call received, appointment set, lead created, etc) of their inbound funnel is at that moment for the current week (probably a date range selector can be used), giving a visual feedback with just colors depending of how it compares to their "typical" numbers. By default this resume would be for all the customer locations, you can apply a selector to check the resume for a specific location.
- a section that list the locations where the customer would need to pay specific atention. Each item give a summarized explanation of what is abnormal with that location.
    - The process to know if a location have an issue can have two base steps: one it's aggregate the data given some parameters/filters, two is decide based on the data if this can be marked as "normal" or not based on some simple bussiness rules.

## Where would an LLM fit?

I think an LLM could be used in the second section to generate a simple explanation of why a location needs attention. The LLM could analyze the results and generate a short explanation of what is unusual and why the location was flagged.

## Tech stack

I would go with a React app for building the dashboard, and Django+DRF for building the API. Postgresql as the db.

## Base data models

Two tables:
- accounts — one row per customer. Includes the account's IANA timezone.
- activity_events — inbound activity: call_received, lead_created, appointment_set. Each event has a location (the account's site/branch), an occurred_at timestamp in UTC, an optional duration_seconds (calls), and an optional outcome.

## Implementation plan

- Project setup
    - set up the project structure (React frontend + Django/DRF backend).
    - create a Docker Compose setup to run the application and database.
    - Configure environment variables and basic dependencies.
- DB setup
    - Implement the base Django models based on the provided schema (Base data models section).
    - Create migrations.
    - Create a custom command to populate the db using the seed.sql file.
- API implementation
    - Implement the endpoint to retrieve the weekly activity summary.
    - Implement location filters.
    - Build the aggregation queries.
    - Implement the logic to compare current activity against historical.
    - Implement location anomaly detection and generate explanations.
    - Add API tests.
- Dashboard implementation
    - Build the dashboard layout and component structure.
    - Implement the weekly activity overview with color-coded comparisons.
    - Add location selectors.
    - Build the section listing locations that need attention.
    - Display a summarized explanation for each flagged location.
    - Connect the dashboard to the backend API.
- Integration and validation
    - Test the complete flow from database to dashboard.
    - Test edge cases (missing historical data, zero activity, multiple locations).
    - Fix any integration issues and polish UI.
