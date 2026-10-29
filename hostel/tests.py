
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (
    Student,
    Room,
    Allocation,
    LeaveRequest,
    FeeInvoice,
    PaymentRecord,
    Complaint,
    VisitorLog,
    MealAttendance,
    Notice,
    AuditEvent,
)

User = get_user_model()


class HostelModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="adminuser",
            password="password123",
            is_staff=True,
            is_superuser=True,
        )

        self.student = Student.objects.create(
            student_id="HMS001",
            full_name="Test Student",
            email="student@example.com",
            status="ACTIVE",
        )

        self.room = Room.objects.create(
            block="A",
            room_number="101",
            capacity=1,
        )

    # TC-01: Django configuration
    def test_django_configuration(self):
        from django.core.management import call_command

        call_command("check")

    # TC-02: Dashboard and health endpoint
    def test_home_page_returns_dashboard(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hostel Management System")
        self.assertContains(response, "Student records")

    def test_dashboard_only_displays_published_notices(self):
        Notice.objects.create(
            title="Published Sprint 2 notice",
            message="This notice is visible.",
            published=True,
            created_by=self.user,
        )
        Notice.objects.create(
            title="Unpublished Sprint 2 draft",
            message="This draft is not visible.",
            published=False,
            created_by=self.user,
        )

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Published Sprint 2 notice")
        self.assertNotContains(response, "Unpublished Sprint 2 draft")

    def test_health_endpoint(self):
        response = self.client.get(reverse("health"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    # TC-03: Student
    def test_create_student_record(self):
        student = Student.objects.create(
            student_id="HMS002",
            full_name="John Doe",
            email="john@example.com",
            status="ACTIVE",
            phone="9876543210",
        )

        self.assertEqual(
            Student.objects.filter(student_id="HMS002").count(),
            1,
        )
        self.assertEqual(str(student), "HMS002 — John Doe")

    # TC-04: Room
    def test_room_starts_with_capacity_available(self):
        self.assertEqual(self.room.available_beds, 1)

    def test_create_room_record(self):
        room = Room.objects.create(
            block="B",
            room_number="202",
            capacity=2,
            room_type="PREMIUM",
        )

        self.assertEqual(
            Room.objects.filter(block="B", room_number="202").count(),
            1,
        )
        self.assertEqual(str(room), "Block B / Room 202")

    # TC-05: Allocation
    def test_allocation_uses_room_capacity(self):
        allocation = Allocation.objects.create(
            student=self.student,
            room=self.room,
            bed_label="Bed 1",
        )

        self.room.refresh_from_db()

        self.assertEqual(self.room.available_beds, 0)
        self.assertEqual(allocation.student, self.student)
        self.assertEqual(allocation.room, self.room)

    def test_database_prevents_double_allocation_of_same_bed(self):
        Allocation.objects.create(
            student=self.student,
            room=self.room,
            bed_label="Bed 1",
        )

        second_student = Student.objects.create(
            student_id="HMS002",
            full_name="Second Student",
            email="second@example.com",
            status="ACTIVE",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Allocation.objects.create(
                    student=second_student,
                    room=self.room,
                    bed_label="Bed 1",
                )

    # TC-06: Invoice
    def test_create_invoice(self):
        invoice = FeeInvoice.objects.create(
            student=self.student,
            description="Monthly Hostel Fee",
            amount=Decimal("5000.00"),
            due_date=date.today() + timedelta(days=30),
            status="UNPAID",
        )

        self.assertEqual(
            FeeInvoice.objects.filter(student=self.student).count(),
            1,
        )
        self.assertEqual(invoice.status, "UNPAID")
        self.assertEqual(invoice.amount, Decimal("5000.00"))

    # TC-07: Payment
    def test_add_payment_record(self):
        invoice = FeeInvoice.objects.create(
            student=self.student,
            description="Semester Fee",
            amount=Decimal("10000.00"),
            due_date=date.today() + timedelta(days=15),
            status="UNPAID",
        )

        payment = PaymentRecord.objects.create(
            invoice=invoice,
            amount=Decimal("5000.00"),
            mode="CASH",
            reference="REC12345",
            recorded_by=self.user,
        )

        self.assertEqual(
            PaymentRecord.objects.filter(invoice=invoice).count(),
            1,
        )
        self.assertEqual(payment.amount, Decimal("5000.00"))
        self.assertEqual(payment.recorded_by, self.user)

    # TC-08: Fee balance
    def test_fee_balance_calculation(self):
        invoice = FeeInvoice.objects.create(
            student=self.student,
            description="Annual Mess Fee",
            amount=Decimal("12000.00"),
            due_date=date.today() + timedelta(days=30),
            status="UNPAID",
        )

        PaymentRecord.objects.create(
            invoice=invoice,
            amount=Decimal("4000.00"),
            mode="ONLINE",
            reference="TXN001",
            recorded_by=self.user,
        )

        PaymentRecord.objects.create(
            invoice=invoice,
            amount=Decimal("3000.00"),
            mode="CASH",
            reference="REC002",
            recorded_by=self.user,
        )

        total_paid = (
            invoice.payments.aggregate(total=models.Sum("amount"))["total"]
            or Decimal("0.00")
        )
        balance = invoice.amount - total_paid

        self.assertEqual(balance, Decimal("5000.00"))

    # TC-09: Complaint
    def test_create_update_complaint(self):
        complaint = Complaint.objects.create(
            student=self.student,
            category="PLUMBING",
            description="Leaking tap in bathroom",
            status="OPEN",
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
            student=self.student,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3),
            reason="Festival break",
            status="PENDING",
        )

        self.assertEqual(leave.status, "PENDING")
        self.assertEqual(leave.student, self.student)

    def test_leave_end_date_cannot_precede_start_date(self):
        leave = LeaveRequest(
            student=self.student,
            start_date=date.today(),
            end_date=date.today() - timedelta(days=1),
            reason="Family visit",
        )

        with self.assertRaises(ValidationError):
            leave.full_clean()

    # TC-11: Visitor log
    def test_add_visitor_entry(self):
        visitor = VisitorLog.objects.create(
            student=self.student,
            visitor_name="Jane Smith",
            visitor_phone="9988776655",
            purpose="Parent Visit",
        )

        self.assertEqual(
            VisitorLog.objects.filter(student=self.student).count(),
            1,
        )
        self.assertEqual(visitor.visitor_name, "Jane Smith")

    def test_record_visitor_exit_time(self):
        visitor = VisitorLog.objects.create(
            student=self.student,
            visitor_name="Jane Smith",
        )
        exit_time = timezone.now()

        visitor.exit_time = exit_time
        visitor.save()
        visitor.refresh_from_db()

        self.assertEqual(visitor.exit_time, exit_time)

    # TC-12: Meal attendance
    def test_record_meal_attendance(self):
        meal = MealAttendance.objects.create(
            student=self.student,
            date=date.today(),
            meal="LUNCH",
            present=True,
        )

        self.assertEqual(
            MealAttendance.objects.filter(
                student=self.student,
                meal="LUNCH",
            ).count(),
            1,
        )
        self.assertTrue(meal.present)

    def test_meal_attendance_prevents_duplicate_student_meal_date(self):
        MealAttendance.objects.create(
            student=self.student,
            date=date.today(),
            meal="LUNCH",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                MealAttendance.objects.create(
                    student=self.student,
                    date=date.today(),
                    meal="LUNCH",
                )

    # TC-13: Notice
    def test_create_notice(self):
        notice = Notice.objects.create(
            title="Hostel Inspection",
            message="Annual inspection scheduled for Monday.",
            published=True,
            created_by=self.user,
        )

        self.assertEqual(
            Notice.objects.filter(created_by=self.user).count(),
            1,
        )
        self.assertTrue(notice.published)

    # TC-14: Audit event record
    def test_audit_event_logged(self):
        audit = AuditEvent.objects.create(
            actor=self.user,
            action="CREATE",
            object_type="Student",
            object_id=str(self.student.pk),
            details={"student_id": self.student.student_id},
        )

        self.assertEqual(audit.action, "CREATE")
        self.assertEqual(audit.details["student_id"], "HMS001")

    # TC-15: Admin student creation is audited
    def test_admin_student_creation_is_audited(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("admin:hostel_student_add"),
            {
                "student_id": "HMS003",
                "full_name": "Admin Created Student",
                "email": "admincreated@example.com",
                "status": "ACTIVE",
                "_save": "Save",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        student = Student.objects.get(student_id="HMS003")

        self.assertTrue(
            AuditEvent.objects.filter(
                actor=self.user,
                action="CREATE",
                object_type="Student",
                object_id=str(student.pk),
            ).exists()
        )

    # TC-16: Admin student update is audited
    def test_admin_student_update_is_audited(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "admin:hostel_student_change",
                args=[self.student.pk],
            ),
            {
                "student_id": self.student.student_id,
                "full_name": "Updated Student Name",
                "email": self.student.email,
                "status": self.student.status,
                "phone": self.student.phone or "",
                "course": self.student.course or "",
                "guardian_name": self.student.guardian_name or "",
                "guardian_phone": self.student.guardian_phone or "",
                "_save": "Save",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            AuditEvent.objects.filter(
                actor=self.user,
                action="UPDATE",
                object_type="Student",
                object_id=str(self.student.pk),
            ).exists()
        )

    # TC-17: Admin bulk deletion is audited
    def test_admin_bulk_delete_creates_audit_events(self):
        self.client.force_login(self.user)

        second_student = Student.objects.create(
            student_id="HMS002",
            full_name="Second Student",
            email="second@example.com",
            status="ACTIVE",
        )

        student_ids = [self.student.pk, second_student.pk]

        response = self.client.post(
            reverse("admin:hostel_student_changelist"),
            {
                "action": "delete_selected",
                "_selected_action": [str(pk) for pk in student_ids],
                "post": "yes",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        for student_id in student_ids:
            self.assertTrue(
                AuditEvent.objects.filter(
                    actor=self.user,
                    action="DELETE",
                    object_type="Student",
                    object_id=str(student_id),
                ).exists()
            )

        self.assertFalse(
            Student.objects.filter(pk__in=student_ids).exists()
        )
    # TC-18: Room capacity hardening
    def test_new_allocation_exceeding_room_capacity_with_different_bed_label(self):
        Allocation.objects.create(
            student=self.student,
            room=self.room,
            bed_label="Bed 1",
        )
        second_student = Student.objects.create(
            student_id="HMS002",
            full_name="Second Student",
            email="second@example.com",
            status="ACTIVE",
        )
        allocation = Allocation(
            student=second_student,
            room=self.room,
            bed_label="Bed 2",
        )
        with self.assertRaises(ValidationError) as ctx:
            allocation.full_clean()
        self.assertIn("This room has no available beds.", str(ctx.exception))

    def test_moving_allocation_into_full_room_is_rejected(self):
        alloc1 = Allocation.objects.create(
            student=self.student,
            room=self.room,
            bed_label="Bed 1",
        )
        room_b = Room.objects.create(
            block="B",
            room_number="102",
            capacity=1,
        )
        second_student = Student.objects.create(
            student_id="HMS002",
            full_name="Second Student",
            email="second@example.com",
            status="ACTIVE",
        )
        Allocation.objects.create(
            student=second_student,
            room=room_b,
            bed_label="Bed 1",
        )
        alloc1.room = room_b
        alloc1.bed_label = "Bed 2"
        with self.assertRaises(ValidationError) as ctx:
            alloc1.full_clean()
        self.assertIn("This room has no available beds.", str(ctx.exception))

    def test_updating_allocation_within_current_full_room_succeeds(self):
        alloc = Allocation.objects.create(
            student=self.student,
            room=self.room,
            bed_label="Bed 1",
        )
        alloc.bed_label = "Bed 1-Updated"
        alloc.full_clean()
        alloc.save()
        alloc.refresh_from_db()
        self.assertEqual(alloc.bed_label, "Bed 1-Updated")

    # TC-19: Payment validation hardening
    def test_payment_amount_zero_or_less_rejected(self):
        invoice = FeeInvoice.objects.create(
            student=self.student,
            description="Semester Fee",
            amount=Decimal("5000.00"),
            due_date=date.today() + timedelta(days=15),
            status="UNPAID",
        )
        payment_zero = PaymentRecord(
            invoice=invoice,
            amount=Decimal("0.00"),
            mode="CASH",
            recorded_by=self.user,
        )
        with self.assertRaises(ValidationError) as ctx:
            payment_zero.full_clean()
        self.assertIn("Payment amount must be greater than zero.", str(ctx.exception))

        payment_neg = PaymentRecord(
            invoice=invoice,
            amount=Decimal("-500.00"),
            mode="CASH",
            recorded_by=self.user,
        )
        with self.assertRaises(ValidationError):
            payment_neg.full_clean()

    def test_payment_exceeding_remaining_invoice_balance_rejected(self):
        invoice = FeeInvoice.objects.create(
            student=self.student,
            description="Mess Fee",
            amount=Decimal("5000.00"),
            due_date=date.today() + timedelta(days=15),
            status="UNPAID",
        )
        PaymentRecord.objects.create(
            invoice=invoice,
            amount=Decimal("3000.00"),
            mode="CASH",
            recorded_by=self.user,
        )
        excess_payment = PaymentRecord(
            invoice=invoice,
            amount=Decimal("2500.00"),
            mode="ONLINE",
            recorded_by=self.user,
        )
        with self.assertRaises(ValidationError) as ctx:
            excess_payment.full_clean()
        self.assertIn("exceeds outstanding balance", str(ctx.exception))

    def test_payment_exactly_equal_to_remaining_balance_succeeds(self):
        invoice = FeeInvoice.objects.create(
            student=self.student,
            description="Hostel Fee",
            amount=Decimal("5000.00"),
            due_date=date.today() + timedelta(days=15),
            status="UNPAID",
        )
        PaymentRecord.objects.create(
            invoice=invoice,
            amount=Decimal("3000.00"),
            mode="CASH",
            recorded_by=self.user,
        )
        exact_payment = PaymentRecord(
            invoice=invoice,
            amount=Decimal("2000.00"),
            mode="CASH",
            recorded_by=self.user,
        )
        exact_payment.full_clean()
        exact_payment.save()

        # Updating payment excludes itself from sum
        exact_payment.amount = Decimal("1500.00")
        exact_payment.full_clean()
        exact_payment.save()
        self.assertEqual(exact_payment.amount, Decimal("1500.00"))

    # TC-20: Visitor timestamp validation hardening
    def test_visitor_exit_time_earlier_than_entry_time_rejected(self):
        now = timezone.now()
        visitor = VisitorLog(
            student=self.student,
            visitor_name="Jane Doe",
            entry_time=now,
            exit_time=now - timedelta(minutes=30),
        )
        with self.assertRaises(ValidationError) as ctx:
            visitor.full_clean()
        self.assertIn("Exit time cannot be earlier than entry time.", str(ctx.exception))

    def test_visitor_valid_exit_time_and_missing_exit_time_succeed(self):
        now = timezone.now()
        ongoing = VisitorLog(
            student=self.student,
            visitor_name="Ongoing Visitor",
            entry_time=now,
            exit_time=None,
        )
        ongoing.full_clean()
        ongoing.save()
        self.assertIsNone(ongoing.exit_time)

        completed = VisitorLog(
            student=self.student,
            visitor_name="Completed Visitor",
            entry_time=now - timedelta(hours=2),
            exit_time=now - timedelta(hours=1),
        )
        completed.full_clean()
        completed.save()
        self.assertGreater(completed.exit_time, completed.entry_time)
