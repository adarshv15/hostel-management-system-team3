# Architecture overview

Browser → Django URL/view layer → hostel business models and validation → relational database.

Django Admin provides the initial authenticated management interface. The dashboard displays aggregate counts. GitHub Actions checks configuration, applies migrations to a clean CI database, and runs the automated test suite.

## Current design decisions
- Django modular monolith for a manageable mini-project.
- SQLite for local setup; choose PostgreSQL/MySQL if required for deployment.
- Built-in Django authentication and admin rather than custom password storage.
- No live payment, email/SMS, or SIS integration in this starter.
