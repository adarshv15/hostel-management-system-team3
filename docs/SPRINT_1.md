# Sprint 1 — Proposed implementation plan

Confirm this backlog with the project guide before treating it as approved.

## Candidate stories
1. Create Django project and CI workflow.
2. Add Student and Room data models.
3. Record allocations and prevent duplicate active bed allocation.
4. Add authenticated administration UI through Django Admin.
5. Add unit tests for room capacity, allocation constraints, dashboard and health endpoint.
6. Add setup instructions and keep SRS/SAD/STP in docs.

## Acceptance checks
- `python manage.py check` succeeds.
- `python manage.py migrate` succeeds.
- `python manage.py test` succeeds.
- GitHub Actions runs on push and pull request.
- README contains reproducible setup instructions.
