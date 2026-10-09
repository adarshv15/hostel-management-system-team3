from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import (
    Student, Room, Allocation, LeaveRequest, FeeInvoice,
    PaymentRecord, Complaint, VisitorLog, MealAttendance, Notice, AuditEvent
)

User = get_user_model()


class HostelModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="adminuser", password="password123")
        self.student = Student.objects.create(
            student_id="HMS001", full_name="Test Student",
            email="student@example.com", status="ACTIVE"
        )
        self.room = Room.objects.create(block="A", room_number="101", capacity=1)

    # TC-01: Django Configuration Check
    def test_django_configuration(self):
        from django.core.management import call_command
        # Should raise no exception
        call_command("check")

    # TC-02: Dashboard
    def test_home_page_returns_dashboard(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hostel Management System")
        self.assertContains(response, "Student records")

    def test_health_endpoint(self):
        response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    # TC-03: Student
    def test_create_student_record(self):
        student2 = Student.objects.create(
            student_id="HMS002", full_name="John Doe",
            email="john@example.com", status="ACTIVE", phone="9876543210"
        )
        self.assertEqual(Student.objects.filter(student_id="HMS002").count(), 1)
        self.assertEqual(str(student2), "HMS002 — John Doe")

    # TC-04: Room
    def test_room_starts_with_capacity_available(self):
        self.assertEqual(self.room.available_beds, 1)

    def test_create_room_record(self):
        room2 = Room.objects.create(block="B", room_number="202", capacity=2, room_type="PREMIUM")
        self.assertEqual(Room.objects.filter(block="B", room_number="202").count(), 1)
        self.assertEqual(str(room2), "Block B / Room 202")

    # TC-05: Allocation
    def test_allocation_uses_room_capacity(self):
        allocation = Allocation.objects.create(student=self.student, room=self.room, bed_label="Bed 1")
        self.room.refresh_from_db()
        self.assertEqual(self.room.available_beds, 0)
        self.assertEqual(allocation.student, self.student)
        self.assertEqual(allocation.room, self.room)

    def test_database_prevents_double_allocation_of_same_bed(self):
        Allocation.objects.create(student=self.student, room=self.room, bed_label="Bed 1")
        second_student = Student.objects.create(
            student_id="HMS002", full_name="Second Student",
            email="second@example.com", status="ACTIVE"
        )
        with self.assertRaises(Exception):
            Allocation.objects.create(student=second_student, room=self.room, bed_label="Bed 1")

    # TC-06: Invoice
    def test_create_invoice(self):
        invoice = FeeInvoice.objects.create(
            student=self.student, description="Monthly Hostel Fee",
            amount=Decimal("5000.00"), due_date=date.today() + timedelta(days=30),
            status="UNPAID"
        )
        self.assertEqual(FeeInvoice.objects.filter(student=self.student).count(), 1)
        self.assertEqual(invoice.status, "UNPAID")
        self.assertEqual(invoice.amount, Decimal("5000.00"))

    # TC-07: Payment
    def test_add_payment_record(self):
        invoice = FeeInvoice.objects.create(
            student=self.student, description="Semester Fee",
            amount=Decimal("10000.00"), due_date=date.today() + timedelta(days=15),
            status="UNPAID"
        )
        payment = PaymentRecord.objects.create(
            invoice=invoice, amount=Decimal("5000.00"), mode="CASH",
            reference="REC12345", recorded_by=self.user
        )
        self.assertEqual(PaymentRecord.objects.filter(invoice=invoice).count(), 1)
        self.assertEqual(payment.amount, Decimal("5000.00"))
        self.assertEqual(payment.recorded_by, self.user)

    # TC-08: Fee balance
    def test_fee_balance_calculation(self):
        invoice = FeeInvoice.objects.create(
            student=self.student, description="Annual Mess Fee",
            amount=Decimal("12000.00"), due_date=date.today() + timedelta(days=30),
            status="UNPAID"
        )
        PaymentRecord.objects.create(
            invoice=invoice, amount=Decimal("4000.00"), mode="ONLINE",
            reference="TXN001", recorded_by=self.user
        )
        PaymentRecord.objects.create(
            invoice=invoice, amount=Decimal("3000.00"), mode="CASH",
            reference="REC002", recorded_by=self.user
        )
        total_paid = invoice.payments.aggregate(total=models.Sum("amount"))["total"] or Decimal("0.00")
        balance = invoice.amount - total_paid
        self.assertEqual(balance, Decimal("5000.00"))

    # TC-09: Complaint
    def test_create_update_complaint(self):
        complaint = Complaint.objects.create(
            student=self.student, category="PLUMBING",
            description="Leaking tap in bathroom", status="OPEN"
        )
        self.assertEqual(complaint.status, "OPEN")
        complaint.status = "RESOLVED"
        complaint.assigned_to = self.user
        complaint.save()
        complaint.refresh_from_db()
        self.assertEqual(complaint.status, "RESOLVED")
        self.assertEqual(complaint.assigned_to, self.user)

    # TC-10: Leave request
    def test_create_leave_request(self):
        leave = LeaveRequest.objects.create(
            student=self.student, start_date=date.today(),
            end_date=date.today() + timedelta(days=3), reason="Festival break",
            status="PENDING"
        )
        self.assertEqual(leave.status, "PENDING")
        self.assertEqual(leave.student, self.student)

    def test_leave_end_date_cannot_precede_start_date(self):
        request = LeaveRequest(
            student=self.student, start_date=date.today(),
            end_date=date.today() - timedelta(days=1), reason="Family visit"
        )
        with self.assertRaises(ValidationError):
            request.full_clean()

    # TC-11: Visitor log
    def test_add_visitor_entry(self):
        visitor = VisitorLog.objects.create(
            student=self.student, visitor_name="Jane Smith",
            visitor_phone="9988776655", purpose="Parent Visit"
        )
        self.assertEqual(VisitorLog.objects.filter(student=self.student).count(), 1)
        self.assertEqual(visitor.visitor_name, "Jane Smith")

    # TC-12: Meal attendance
    def test_record_meal_attendance(self):
        meal = MealAttendance.objects.create(
            student=self.student, date=date.today(), meal="LUNCH", present=True
        )
        self.assertEqual(MealAttendance.objects.filter(student=self.student, meal="LUNCH").count(), 1)
        self.assertTrue(meal.present)

    # TC-13: Notice
    def test_create_notice(self):
        notice = Notice.objects.create(
            title="Hostel Inspection", message="Annual inspection scheduled for Monday.",
            published=True, created_by=self.user
        )
        self.assertEqual(Notice.objects.filter(created_by=self.user).count(), 1)
        self.assertTrue(notice.published)

    # TC-14: Audit log
    def test_audit_event_logged(self):
        audit = AuditEvent.objects.create(
            actor=self.user, action="CREATE", object_type="Student",
            object_id=str(self.student.pk), details={"student_id": self.student.student_id}
        )
        self.assertEqual(AuditEvent.objects.filter(object_type="Student").count(), 1)
        self.assertEqual(audit.action, "CREATE")
        self.assertEqual(audit.details["student_id"], "HMS001")
    
    # Sharath's contribution: additional business-rule validation tests

    def test_inactive_student_cannot_be_allocated_a_bed(self):
        inactive_student = Student.objects.create(
            student_id="HMS003",
            full_name="Inactive Student",
            email="inactive@example.com",
            status="INACTIVE",
        )

        allocation = Allocation(
            student=inactive_student,
            room=self.room,
            bed_label="Bed 1",
        )

        with self.assertRaises(ValidationError):
            allocation.full_clean()

    def test_full_room_rejects_another_allocation(self):
        Allocation.objects.create(
            student=self.student,
            room=self.room,
            bed_label="Bed 1",
        )

        second_student = Student.objects.create(
            student_id="HMS004",
            full_name="Second Student",
            email="second@example.com",
            status="ACTIVE",
        )

        allocation = Allocation(
            student=second_student,
            room=self.room,
            bed_label="Bed 2",
        )

        with self.assertRaises(ValidationError):
            allocation.full_clean()

    def test_leave_request_for_single_day_is_valid(self):
        leave = LeaveRequest(
            student=self.student,
            start_date=date.today(),
            end_date=date.today(),
            reason="One-day personal leave",
        )

        leave.full_clean()
    
    # Additional business-rule tests contributed by Sharath

    def test_inactive_student_cannot_be_allocated_a_bed(self):
        inactive_student = Student.objects.create(
            student_id="HMS003",
            full_name="Inactive Student",
            email="inactive@example.com",
            status="INACTIVE",
        )
        allocation = Allocation(
            student=inactive_student,
            room=self.room,
            bed_label="Bed 1",
        )

        with self.assertRaises(ValidationError):
            allocation.full_clean()

    def test_full_room_rejects_another_allocation(self):
        Allocation.objects.create(
            student=self.student,
            room=self.room,
            bed_label="Bed 1",
        )
        second_student = Student.objects.create(
            student_id="HMS004",
            full_name="Second Student",
            email="second@example.com",
            status="ACTIVE",
        )
        allocation = Allocation(
            student=second_student,
            room=self.room,
            bed_label="Bed 2",
        )

        with self.assertRaises(ValidationError):
            allocation.full_clean()

    def test_leave_request_for_single_day_is_valid(self):
        leave = LeaveRequest(
            student=self.student,
            start_date=date.today(),
            end_date=date.today(),
            reason="One-day personal leave",
        )
        leave.full_clean()
