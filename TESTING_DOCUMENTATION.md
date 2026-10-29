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

### Results recorded on October 29, 2026

Executed with the local Python 3.12 interpreter:

| Command | Result |
|---|---|
| `python manage.py check` | Passed: no issues reported (0 silenced). |
| `python manage.py test` | Passed: 32 tests in 44.846 seconds. |

The test runner creates and destroys its test database. It does not require
resetting the local development database.

## Automated coverage

See [docs/TEST_CASES.md](docs/TEST_CASES.md) for the requirement-to-test
mapping. In brief, the automated suite covers:
- Fee invoices and payment records, including validation that payments are strictly positive, do not exceed the remaining balance, and exclude updating payments from the remaining balance sum.
- Room allocations, including capacity tracking, bed uniqueness, rejection of allocations beyond capacity, rejection of moves into full rooms, and valid in-place updates.
- Complaints and leave request date ordering.
- Visitor logs, including exit-after-entry validation and ongoing visit handling.
- Meal attendance uniqueness per student, meal, and date.
- Published versus draft notice visibility on the dashboard.
- Administrative audit event creation for create, update, and bulk deletion.
- Dashboard, health endpoint, student records, room inventory, and configuration regression checks.

## Manual checks reported by the project owner

The project owner reports having manually verified dashboard access, admin
login, student creation, audit logging, room creation, and room allocation
with correct occupancy. These checks were not independently repeated during
the automated test run in this report.

## Limits of this test record

- Automated tests use Django's test client and temporary database, not a
  deployed environment or real user accounts.
- Model validations in `clean()` are executed during Django Admin and ModelForm
  workflows. Direct ORM calls (`objects.create()` or `.save()`) do not call `clean()`
  automatically without explicit `full_clean()`.
- Payment records are administrative records; no live payment gateway is
  connected, and `FeeInvoice.status` is not automatically transitioned upon payment.
- This report does not claim role-specific student workflows, production
  deployment, or untested SRS acceptance criteria are complete.
- No code coverage measurement was run for this report.
