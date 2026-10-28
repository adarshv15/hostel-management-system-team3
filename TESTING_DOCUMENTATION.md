# Sprint 2 Testing Documentation

**Project:** Hostel Management System (HMS) — Team 3  
**Test framework:** Django `TestCase` and Django's test runner
**Local test database:** Django-managed temporary test database

## Test execution

Run these commands from the repository root:

```powershell
python manage.py check
python manage.py test
```

### Results recorded on October 28, 2026

Executed with the repository's `.venv` interpreter (Python 3.13.7):

| Command | Result |
|---|---|
| `python manage.py check` | Passed: no issues reported (0 silenced). |
| `python manage.py test` | Passed: 24 tests in 26.783 seconds. |

The test runner creates and destroys its test database. It does not require
resetting the local development database.

## Automated coverage

See [docs/TEST_CASES.md](docs/TEST_CASES.md) for the requirement-to-test
mapping. In brief, the automated suite covers fee invoices and payments,
complaints, leave validation, visitor records, meal attendance uniqueness,
notices, and administrative audit-event creation, in addition to the earlier
student, room, allocation, dashboard, health, and configuration regression
checks. Audit tests cover admin-created student records, updates, and bulk
deletions; individual deletion and non-admin write paths are not covered.

The fee balance test computes the balance from recorded payments. It does not
demonstrate payment gateway integration or enforcement that payments cannot
exceed an invoice. The notice test checks published-versus-unpublished
visibility, not every notice ordering or limit.

## Manual checks reported by the project owner

The project owner reports having manually verified dashboard access, admin
login, student creation, audit logging, room creation, and room allocation
with correct occupancy. These checks were not independently repeated during
the automated test run in this report.

## Limits of this test record

- Automated tests use Django's test client and temporary database, not a
  deployed environment or real user accounts.
- Payment records are administrative records; no live payment gateway is
  connected.
- This report does not claim role-specific student workflows, production
  deployment, or untested SRS acceptance criteria are complete.
- No code coverage measurement was run for this report.
