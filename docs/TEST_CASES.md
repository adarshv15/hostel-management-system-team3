# Automated Test Case Coverage

The regression tests are implemented in `hostel/tests.py` and use Django's
`TestCase`. Run the full suite with `python manage.py test`.

| Requirement | Covered scenarios | Test methods |
|---|---|---|
| Fees and payments | Invoice creation, payment recording, and outstanding balance calculation | `test_create_invoice`, `test_add_payment_record`, `test_fee_balance_calculation` |
| Complaints | Create a complaint, assign it, and update its status | `test_create_update_complaint` |
| Leave requests | Create a pending request and reject an end date earlier than the start date | `test_create_leave_request`, `test_leave_end_date_cannot_precede_start_date` |
| Visitor logs | Record visitor entry and persist an exit time | `test_add_visitor_entry`, `test_record_visitor_exit_time` |
| Meal attendance | Record attendance and reject a duplicate student/meal/date tuple | `test_record_meal_attendance`, `test_meal_attendance_prevents_duplicate_student_meal_date` |
| Notices | Create a notice; show published notices and hide unpublished drafts on the dashboard | `test_create_notice`, `test_dashboard_only_displays_published_notices` |
| Audit logging | Store an audit event; verify admin student creation, update, and bulk deletion create audit events | `test_audit_event_logged`, `test_admin_student_creation_is_audited`, `test_admin_student_update_is_audited`, `test_admin_bulk_delete_creates_audit_events` |
| Regression checks | Dashboard and health endpoint, student, room, allocation, and configuration checks | See `hostel/tests.py` |

These are automated model and Django test-client checks, not end-to-end testing
with real users or a production database. Manual checks should be documented
separately from automated results.
