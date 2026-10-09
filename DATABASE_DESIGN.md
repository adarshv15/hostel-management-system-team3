# Hostel Management System — Database Design

## 1. Purpose

This document describes the main data entities, relationships, business rules, and data-integrity considerations for the Hostel Management System (HMS).

The system manages student records, room allocation, fee payments, complaints, leave requests, visitor logs, meal attendance, notices, and audit events.

## 2. Main Models

| Model | Purpose |
|---|---|
| `Student` | Stores student-related information and records. |
| `Room` | Stores hostel room details and capacity information. |
| `Allocation` | Connects students to rooms and records allocation details. |
| `FeeInvoice` | Records fee invoices, amounts, due dates, and payment status. |
| `PaymentRecord` | Stores individual payments, payment mode, reference, and recording user. |
| `Complaint` | Records student complaints and their status. |
| `LeaveRequest` | Stores leave dates, request details, and status. |
| `VisitorLog` | Records visitor information and visit details. |
| `MealAttendance` | Tracks meal attendance records. |
| `Notice` | Stores notices published for users. |
| `AuditEvent` | Records activity information such as actor, action, object type, object ID, and timestamp. |

The exact fields, database column names, constraints, and relationships should be verified against `hostel/models.py` and the project's migrations.

## 3. Key Relationships

### 3.1 Students, Rooms, and Allocations

The `Allocation` model connects students with rooms. It is the central record for tracking room assignments.

Important integrity considerations include:

- A student should not be allocated a bed when the student is inactive.
- Room allocations must respect the configured room capacity.
- The same bed should not be allocated to multiple students simultaneously.
- Allocation dates and status should accurately represent the occupancy period.

The exact foreign-key fields and rules for historical allocations must be confirmed from the implementation.

### 3.2 Invoices and Payments

`FeeInvoice` records the amount billed to a student, while `PaymentRecord` stores individual payments.

The relationship between invoices and payments should be verified in the Django models. If multiple payments can be associated with one invoice, the remaining balance can be calculated as:

`Balance Due = Invoice Amount - Total Payments`

The application should handle partial payments and prevent invalid amounts according to its implemented business rules.

### 3.3 Other Records

Complaints, leave requests, visitor logs, meal attendance, notices, and audit events support the daily operation of the hostel.

Their exact relationships with students, users, and other models should be documented from the model definitions rather than assumed.

## 4. Fee Tracking

The outstanding balance is calculated using the invoice amount and payments recorded against that invoice.

For example, if an invoice is ₹10,000 and the recorded payments total ₹6,000:

`Balance Due = ₹10,000 - ₹6,000 = ₹4,000`

This example illustrates the calculation; it does not prescribe a specific invoice amount or currency configuration for the application.

## 5. Data Integrity and Validation

The following rules are important for reliable hostel management:

- **Student eligibility:** Validate student status before allowing a new allocation.
- **Room capacity:** Prevent allocations that exceed the permitted room capacity.
- **Bed uniqueness:** Prevent conflicting active allocations for the same bed.
- **Leave dates:** Reject leave requests whose end date precedes the start date.
- **Payment records:** Validate payment amounts and their association with invoices.
- **Referential integrity:** Use the configured database relationships to maintain valid references between records.
- **Auditability:** Preserve relevant activity information where audit events are recorded.

These are documentation-level expectations. The actual enforcement mechanism may be implemented through model validation, database constraints, views, forms, or other application logic.

## 6. Verification and Maintenance

When the database schema changes, update this document to match the implementation.

Before documenting a field or constraint as guaranteed, verify it against:

1. `hostel/models.py`
2. Migration files under `hostel/migrations/`
3. Relevant automated tests in `hostel/tests.py`

Review the documentation whenever models, relationships, allocation rules, payment handling, or validation behavior change.

## 7. Scope and Limitations

This document summarizes the database design at a conceptual level. It does not replace the Django model definitions or migration history.

Exact field types, nullability, default values, foreign-key deletion behavior, indexes, and uniqueness constraints should be confirmed from the current source code before being treated as definitive.