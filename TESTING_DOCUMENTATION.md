# Hostel Management System — Testing Documentation

**Tester / Responsible Person:** Mohammadnoor Sirasgi (Noor)  
**Project:** Hostel Management System (HMS) — Team 3  
**Execution Date:** October 9, 2026  
**Test Framework:** Django Test Suite (`django.test.TestCase`) & Coverage.py  

---

## Purpose
This document provides a comprehensive report of functional and automated unit/integration testing for the Hostel Management System. All test cases have been executed against the actual Django implementation, and actual results and verification evidence have been recorded below.

---

## Test Execution Summary

- **Total Test Cases Defined:** 14 (TC-01 through TC-14)
- **Automated Test Methods Executed:** 18
- **Tests Passed:** 18 / 18 (100% Pass Rate)
- **Code Coverage Achieved:** 95% overall project coverage (`hostel/tests.py`: 100%, `hostel/models.py`: 90%, `hostel/views.py`: 100%, `hostel/admin.py`: 95%)

---

## Verified Test Cases & Results

| ID | Feature | Test | Expected result | Actual result | Status |
|---|---|---|---|---|---|
| **TC-01** | Django configuration | Run `python manage.py check` | No configuration issues are reported | `System check identified no issues (0 silenced).` Executed via `test_django_configuration`. | **PASS** |
| **TC-02** | Dashboard | Open the homepage/dashboard (`GET /`) | Page loads and summary values are displayed | HTTP 200 returned. Rendered dashboard with summary cards for Student records, Rooms, Allocations, Invoices, Complaints, Leave requests, and Notices. Executed via `test_home_page_returns_dashboard` and `test_health_endpoint`. | **PASS** |
| **TC-03** | Student | Create a student record | Record is saved and visible | Created Student record (`student_id="HMS002"`, `status="ACTIVE"`). Record saved to SQLite DB and string representation `HMS002 — John Doe` verified. Executed via `test_create_student_record`. | **PASS** |
| **TC-04** | Room | Create a room record | Record is saved and visible | Created Room record (`block="B"`, `room_number="202"`, `capacity=2`). Room saved with initial `available_beds = 2`. Executed via `test_create_room_record` and `test_room_starts_with_capacity_available`. | **PASS** |
| **TC-05** | Allocation | Create a valid allocation | Allocation is linked to the correct student/room | Allocation created linking `HMS001` to `Block A / Room 101`. Available beds decremented from 1 to 0. Duplicate bed allocation blocked by DB unique constraint. Executed via `test_allocation_uses_room_capacity` and `test_database_prevents_double_allocation_of_same_bed`. | **PASS** |
| **TC-06** | Invoice | Create an invoice | Amount, due date, and status are displayed | FeeInvoice created (`amount=₹5000.00`, `due_date`, `status="UNPAID"`). Invoice saved and correctly associated with Student `HMS001`. Executed via `test_create_invoice`. | **PASS** |
| **TC-07** | Payment | Add a payment record | Payment is saved and linked to the correct invoice | PaymentRecord created (`amount=₹5000.00`, `mode="CASH"`, `reference="REC12345"`, `recorded_by=adminuser`). Saved and linked to FeeInvoice. Executed via `test_add_payment_record`. | **PASS** |
| **TC-08** | Fee balance | Compare invoice amount and payments | Balance equals invoice amount minus valid recorded payments | Invoice of ₹12,000.00 created with two payments (₹4,000.00 online + ₹3,000.00 cash). Outstanding balance verified as ₹5,000.00 (₹12,000.00 - ₹7,000.00). Executed via `test_fee_balance_calculation`. | **PASS** |
| **TC-09** | Complaint | Create/update a complaint | Saved status is displayed correctly | Complaint created with category `PLUMBING` and status `OPEN`. Status updated to `RESOLVED` and assigned to admin user. Executed via `test_create_update_complaint`. | **PASS** |
| **TC-10** | Leave request | Create a leave request | Request and dates are recorded correctly | LeaveRequest created (`start_date=today`, `end_date=today+3`, `status="PENDING"`). Validation enforced: end date before start date raises `ValidationError`. Executed via `test_create_leave_request` and `test_leave_end_date_cannot_precede_start_date`. | **PASS** |
| **TC-11** | Visitor log | Add a visitor entry | Entry is saved and retrievable | VisitorLog created (`visitor_name="Jane Smith"`, `purpose="Parent Visit"`). Verified saved and retrievable via `student.visitors`. Executed via `test_add_visitor_entry`. | **PASS** |
| **TC-12** | Meal attendance | Record meal attendance | Entry is saved for the correct meal/date | MealAttendance recorded (`meal="LUNCH"`, `present=True`). Database unique constraint `(student, date, meal)` enforced. Executed via `test_record_meal_attendance`. | **PASS** |
| **TC-13** | Notice | Create a notice | Notice is saved and displayed according to project rules | Notice created (`title="Hostel Inspection"`, `published=True`, `created_by=adminuser`). Saved and published. Executed via `test_create_notice`. | **PASS** |
| **TC-14** | Audit log | Create/update a tracked record | Audit event matches the implemented logging logic | AuditEvent created (`action="CREATE"`, `object_type="Student"`, `details={"student_id": "HMS001"}`). Verified event structure, timestamp, and JSON metadata. Executed via `test_audit_event_logged`. | **PASS** |

---

## Detailed Test Case Execution Record

### Test Environment
- **OS:** Windows 11 / PowerShell
- **Python Version:** 3.12.10
- **Django Version:** 5.2.18
- **Database:** SQLite 3 (`db.sqlite3` / memory test database)

### How to Run Automated Checks & Tests

From the repository root (`hostel-management-system-team3`), run:

```powershell
# 1. Check Django configuration
python manage.py check

# 2. Run Django automated test suite
python manage.py test

# 3. Run coverage report
coverage run manage.py test
coverage report
```

### Output Evidence

#### 1. Configuration Check (`python manage.py check`)
```text
System check identified no issues (0 silenced).
```

#### 2. Test Runner (`python manage.py test`)
```text
Creating test database for alias 'default'...
..................
----------------------------------------------------------------------
Ran 18 tests in 17.622s

OK
Destroying test database for alias 'default'...
```

#### 3. Code Coverage (`coverage report`)
```text
Name                                Stmts   Miss  Cover
-------------------------------------------------------
hms_project\__init__.py                 0      0   100%
hms_project\settings.py                25      0   100%
hms_project\urls.py                     4      0   100%
hostel\__init__.py                      0      0   100%
hostel\admin.py                        62      3    95%
hostel\apps.py                          4      0   100%
hostel\migrations\0001_initial.py       9      0   100%
hostel\migrations\__init__.py           0      0   100%
hostel\models.py                      135     14    90%
hostel\tests.py                       100      0   100%
hostel\views.py                         8      0   100%
manage.py                              11      2    82%
-------------------------------------------------------
TOTAL                                 358     19    95%
```

---

## Important Business Logic Verification Notes
- **Invoice & Payment Integrity:** Confirmed that payments link via Foreign Key to `FeeInvoice` and that fee balance calculations correctly deduct payments from total invoice amounts.
- **Room Bed Allocation:** Confirmed that room available beds property dynamically updates when active allocations are added, and database unique constraints prevent double allocation of the same bed.
- **Model Validation:** Verified model-level validation (such as `LeaveRequest` date range validation) prevents corrupt data from saving.
- **Audit Logging:** Verified `AuditEvent` structure captures actor, action, object_type, object_id, and JSON details.

---

## Review & Verification Summary
1. All 14 functional test cases were executed and verified against the actual Django codebase.
2. Actual results column has been filled with concrete, empirical test results.
3. All 14 test cases marked as **PASS**.
4. Test suite expanded in `hostel/tests.py` from 6 initial tests to 18 comprehensive tests.
5. Migration file `0001_initial.py` and `manage.py` configured for setup.
