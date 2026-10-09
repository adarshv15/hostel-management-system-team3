# Hostel Management System — Database Design

## Purpose
This document outlines the main data entities used by the Hostel Management System (HMS).

## Main Models
- **Student** — student-related records.
- **Room** — hostel room records.
- **Allocation** — connects students with rooms and stores allocation details.
- **FeeInvoice** — fee invoices, including amount, due date, and payment status.
- **PaymentRecord** — individual payments, including amount, mode, reference, and the user who recorded the payment.
- **Complaint** — complaints and their status.
- **LeaveRequest** — leave requests and relevant dates/status.
- **VisitorLog** — visitor records.
- **MealAttendance** — meal attendance records.
- **Notice** — notices for users.
- **AuditEvent** — activity records, including actor, action, object type, object ID, timestamp, and details.

> Verify exact fields and foreign-key names in `hostel/models.py` before adding implementation-specific details.

## Key Relationships
- **Student ↔ Allocation ↔ Room:** allocations connect students and rooms.
- **FeeInvoice → PaymentRecord:** payment records represent payments associated with invoices. Confirm the exact relationship field in the model code.
- **AuditEvent:** records relevant actions; the actor may not be populated for every event source.

## Fee Tracking
The remaining balance can be calculated as:

`Balance Due = Invoice Amount - Total Payments`

The invoice status may be Unpaid, Partial, Paid, or Overdue. Verify that the displayed status agrees with the payment records and the project's status-update logic.

## Why the Database Design Matters
The database connects student, room, and allocation records; supports fee tracking; and stores complaints, leave requests, visitors, meal attendance, notices, and audit activity.

## Review Tasks
1. Verify model fields and relationships in `hostel/models.py`.
2. Create an ER diagram based on the actual foreign keys.
3. Document required fields, choices, and validation rules.
4. Use dummy or sanitized data in examples; do not include personal student/payment details.
