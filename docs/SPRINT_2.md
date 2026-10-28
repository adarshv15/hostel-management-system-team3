# Sprint 2 — Feature and Verification Summary

This document records the Sprint 2 requirements against the current Django
implementation and automated tests. It describes the repository state; it
does not imply that every production or SRS acceptance criterion is complete.

## Requirement status

| Requirement | Existing implementation | Automated verification |
| --- | --- | --- |
| Fees and payments | `FeeInvoice` and `PaymentRecord` models are available in Django Admin. Payments are recorded manually; there is no payment gateway. | Invoice/payment creation and a multi-payment outstanding-balance calculation. |
| Complaints and leave requests | Complaint and leave records are available in Django Admin; leave dates have model validation. | Complaint create/update and valid/invalid leave-date tests. |
| Visitor logs | Visitor records include entry and optional exit timestamps and are available in Django Admin. | Visitor creation and persistence of an exit timestamp. |
| Meal attendance | Attendance is recorded by student, date, and meal; the database enforces uniqueness for that combination. | Attendance creation and duplicate-combination rejection. |
| Notices | Notices are managed in Django Admin; the dashboard selects published notices. | Notice creation and a dashboard test confirming published notices appear while drafts do not. |
| Audit logging | Admin-managed record create, update, and delete operations write `AuditEvent` records; the audit-event admin is read-only. | Tests verify event storage and student creation, update, and bulk deletion through the authenticated admin. Individual deletion and non-admin write paths are not covered. |
| Regression testing | Django test suite covers these records plus students, rooms, allocations, dashboard, health endpoint, and Django configuration. | `python manage.py check` passed with no issues; `python manage.py test` passed all 24 tests. |
| Final documentation | Setup and project context are documented in the README; this page and the test mapping/report capture Sprint 2 status. | Documentation reflects observed code and test results, and separates owner-reported manual checks from tests run in this session. |

For test execution details, see [TESTING_DOCUMENTATION.md](../TESTING_DOCUMENTATION.md).

## Remaining gaps

- There is no dedicated student-facing portal or self-service workflow.
- Payments are records only: no gateway integration or tested rule preventing
  payments from exceeding an invoice amount.
- Audit regression tests cover admin create, update, and bulk deletion; individual
  record deletion and non-admin write paths remain untested.
- Visitor time ordering and production role/permission configuration are not
  established by the current automated tests.
- Production deployment, backups, retention, and environment-specific
  hardening remain outside this sprint's verification.

## Verification boundary

The test runner uses Django's temporary test database. Manual checks reported
by the project owner are listed separately in the testing report and were not
independently repeated for this summary.
