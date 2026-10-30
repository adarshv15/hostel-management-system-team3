# Automated Test Case Coverage

The regression tests are implemented in `hostel/tests.py` and use Django's
`TestCase`. Run the full suite with `python manage.py test`.

| Requirement | Covered scenarios | Test methods |
|---|---|---|
| Fees and payments | Invoice creation, payment recording, balance calculation, rejection of amounts <= 0, rejection of payments exceeding balance, exact balance payment, and update exclusion | `test_create_invoice`, `test_add_payment_record`, `test_fee_balance_calculation`, `test_payment_amount_zero_or_less_rejected`, `test_payment_exceeding_remaining_invoice_balance_rejected`, `test_payment_exactly_equal_to_remaining_balance_succeeds` |
| Complaints | Create a complaint, assign it, and update its status | `test_create_update_complaint` |
| Leave requests | Create a pending request and reject an end date earlier than the start date | `test_create_leave_request`, `test_leave_end_date_cannot_precede_start_date` |
| Visitor logs | Record visitor entry, exit timestamp persistence, rejection of exit time earlier than entry time, and support for ongoing visits (missing exit time) | `test_add_visitor_entry`, `test_record_visitor_exit_time`, `test_visitor_exit_time_earlier_than_entry_time_rejected`, `test_visitor_valid_exit_time_and_missing_exit_time_succeed` |
| Meal attendance | Record attendance and reject a duplicate student/meal/date tuple | `test_record_meal_attendance`, `test_meal_attendance_prevents_duplicate_student_meal_date` |
| Notices | Create a notice; show published notices and hide unpublished drafts on the dashboard | `test_create_notice`, `test_dashboard_only_displays_published_notices` |
| Audit logging | Store an audit event; verify admin student creation, update, and bulk deletion create audit events | `test_audit_event_logged`, `test_admin_student_creation_is_audited`, `test_admin_student_update_is_audited`, `test_admin_bulk_delete_creates_audit_events` |
| Room and allocation | Capacity tracking, allocation usage, duplicate bed prevention, over-allocation rejection on distinct bed label, rejection on moving to full room, and permitted update within current room | `test_room_starts_with_capacity_available`, `test_create_room_record`, `test_allocation_uses_room_capacity`, `test_database_prevents_double_allocation_of_same_bed`, `test_new_allocation_exceeding_room_capacity_with_different_bed_label`, `test_moving_allocation_into_full_room_is_rejected`, `test_updating_allocation_within_current_full_room_succeeds` |
| Regression checks | Dashboard and health endpoint, student model, and Django configuration checks | `test_django_configuration`, `test_home_page_returns_dashboard`, `test_health_endpoint`, `test_create_student_record` |

These are automated model and Django test-client checks, not end-to-end testing
with real users or a production database. Model `clean()` validations are enforced
during Django Admin and ModelForm workflows; direct ORM operations require calling `full_clean()`.
