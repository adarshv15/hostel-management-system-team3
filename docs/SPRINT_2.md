# Sprint 2 — Feature and Verification Summary

This document records the Sprint 2 requirements against the current Django
implementation and automated tests. It describes the repository state; it
does not imply that every production or SRS acceptance criterion is complete.

## Requirement status

| Requirement | Existing implementation | Automated verification |
| --- | --- | --- |
| Fees and payments | `FeeInvoice` and `PaymentRecord` models are available in Django Admin. Payment amounts must be > 0 and cannot exceed outstanding balance. Payments are recorded manually; there is no live gateway or automatic status transition. | Invoice/payment creation, multi-payment balance calculation, rejection of non-positive payments, rejection of overpayments, and exact-balance recording. |
| Complaints and leave requests | Complaint and leave records are available in Django Admin; leave dates have model validation rejecting end dates before start dates. | Complaint create/update and valid/invalid leave-date tests. |
| Visitor logs | Visitor records include entry and optional exit timestamps; model validation rejects exit times earlier than entry times. | Visitor creation, exit timestamp persistence, rejection of exit before entry, and ongoing visit support. |
| Meal attendance | Attendance is recorded by student, date, and meal; the database enforces uniqueness for that combination. | Attendance creation and duplicate-combination rejection. |
| Notices | Notices are managed in Django Admin; the dashboard selects published notices. | Notice creation and a dashboard test confirming published notices appear while drafts do not. |
| Audit logging | Admin-managed record create, update, and delete operations write `AuditEvent` records; the audit-event admin is read-only. | Tests verify event storage and student creation, update, and bulk deletion through the authenticated admin. Individual deletion and non-admin write paths are not covered. |
| Room allocation | Allocations track room capacity; model validation prevents allocating beyond room capacity, moving into full rooms, or double-booking active beds. | Tests verify capacity reduction, duplicate bed prevention, rejection of allocations beyond capacity, rejection of moves to full rooms, and in-place updates. |
| Regression testing | Django test suite covers all records plus students, rooms, allocations, dashboard, health endpoint, and Django configuration. | `python manage.py check` passed with no issues; `python manage.py test` passed all 32 tests. |
| Final documentation | Setup and project context are documented in the README; this page and the test mapping/report capture Sprint 2 status. | Documentation reflects observed code and test results, and separates owner-reported manual checks from tests run in this session. |

For test execution details, see [TESTING_DOCUMENTATION.md](../TESTING_DOCUMENTATION.md).

## Remaining gaps

- There is no dedicated student-facing portal or self-service workflow.
- Payments are administrative records: no live gateway integration and no automatic synchronization between payment totals and `FeeInvoice.status` (status remains an administrative field).
- Model-level `clean()` validations are enforced by Django Admin and form workflows; direct programmatic ORM writes (`objects.create()`, `.save()`) bypass `clean()` unless `full_clean()` is explicitly invoked.
- Audit regression tests cover admin create, update, and bulk deletion; individual record deletion and non-admin write paths remain untested.
- Production deployment, backups, retention, role-based permission groups, and environment-specific hardening remain outside this sprint's verification.

## Verification boundary

The test runner uses Django's temporary test database. Manual checks reported
by the project owner are listed separately in the testing report and were not
independently repeated for this summary.
