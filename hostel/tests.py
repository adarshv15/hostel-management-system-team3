from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from .models import Student, Room, Allocation, LeaveRequest, FeeInvoice, Complaint

class HostelModelTests(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            student_id="HMS001", full_name="Test Student",
            email="student@example.com", status="ACTIVE"
        )
        self.room = Room.objects.create(block="A", room_number="101", capacity=1)

    def test_room_starts_with_capacity_available(self):
        self.assertEqual(self.room.available_beds, 1)

    def test_allocation_uses_room_capacity(self):
        Allocation.objects.create(student=self.student, room=self.room, bed_label="Bed 1")
        self.room.refresh_from_db()
        self.assertEqual(self.room.available_beds, 0)

    def test_database_prevents_double_allocation_of_same_bed(self):
        Allocation.objects.create(student=self.student, room=self.room, bed_label="Bed 1")
        second_student = Student.objects.create(
            student_id="HMS002", full_name="Second Student",
            email="second@example.com", status="ACTIVE"
        )
        with self.assertRaises(Exception):
            Allocation.objects.create(student=second_student, room=self.room, bed_label="Bed 1")

    def test_leave_end_date_cannot_precede_start_date(self):
        request = LeaveRequest(
            student=self.student, start_date=date.today(),
            end_date=date.today() - timedelta(days=1), reason="Family visit"
        )
        with self.assertRaises(ValidationError):
            request.full_clean()

    def test_home_page_returns_dashboard(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hostel Management System")

    def test_health_endpoint(self):
        response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
