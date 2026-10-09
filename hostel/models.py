from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Student(models.Model):
    STATUS_CHOICES = [("PENDING", "Pending"), ("ACTIVE", "Active"), ("REJECTED", "Rejected"), ("INACTIVE", "Inactive")]
    student_id = models.CharField(max_length=30, unique=True)
    full_name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    course = models.CharField(max_length=100, blank=True)
    guardian_name = models.CharField(max_length=120, blank=True)
    guardian_phone = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_id} — {self.full_name}"


class Room(models.Model):
    ROOM_TYPES = [("STANDARD", "Standard"), ("SHARED", "Shared"), ("PREMIUM", "Premium")]
    block = models.CharField(max_length=30, default="A")
    room_number = models.CharField(max_length=20)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default="STANDARD")
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["block", "room_number"], name="unique_room_per_block")]

    def __str__(self):
        return f"Block {self.block} / Room {self.room_number}"

    @property
    def occupied_beds(self):
        return self.allocations.filter(checked_out_at__isnull=True).count()

    @property
    def available_beds(self):
        return max(0, self.capacity - self.occupied_beds)


class Allocation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="allocations")
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name="allocations")
    bed_label = models.CharField(max_length=20, default="Bed 1")
    allocated_at = models.DateTimeField(default=timezone.now)
    checked_out_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["room", "bed_label"], condition=models.Q(checked_out_at__isnull=True), name="unique_active_bed"),
            models.UniqueConstraint(fields=["student"], condition=models.Q(checked_out_at__isnull=True), name="student_one_active_allocation"),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.checked_out_at is None and self.student.status != "ACTIVE":
            raise ValidationError("Only active students can be allocated a bed.")
        if self.checked_out_at is None and self.room.available_beds <= 0 and not self.pk:
            raise ValidationError("This room has no available beds.")

    def __str__(self):
        return f"{self.student} → {self.room} ({self.bed_label})"


class FeeInvoice(models.Model):
    STATUS_CHOICES = [("UNPAID", "Unpaid"), ("PARTIAL", "Partially paid"), ("PAID", "Paid"), ("OVERDUE", "Overdue")]
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="invoices")
    description = models.CharField(max_length=160, default="Hostel fee")
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="UNPAID")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice #{self.pk} — {self.student} — ₹{self.amount}"


class PaymentRecord(models.Model):
    MODES = [("CASH", "Cash"), ("CHEQUE", "Cheque"), ("ONLINE", "Online (reference only)")]
    invoice = models.ForeignKey(FeeInvoice, on_delete=models.PROTECT, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    mode = models.CharField(max_length=10, choices=MODES)
    reference = models.CharField(max_length=100, blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment ₹{self.amount} for invoice {self.invoice_id}"


class Complaint(models.Model):
    CATEGORIES = [("ELECTRICAL", "Electrical"), ("PLUMBING", "Plumbing"), ("CLEANING", "Cleaning"), ("OTHER", "Other")]
    STATUSES = [("OPEN", "Open"), ("IN_PROGRESS", "In progress"), ("RESOLVED", "Resolved")]
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="complaints")
    category = models.CharField(max_length=20, choices=CATEGORIES)
    description = models.TextField()
    status = models.CharField(max_length=15, choices=STATUSES, default="OPEN")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_complaints")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Complaint #{self.pk} — {self.category} — {self.status}"


class LeaveRequest(models.Model):
    STATUSES = [("PENDING", "Pending"), ("APPROVED", "Approved"), ("REJECTED", "Rejected")]
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="leave_requests")
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUSES, default="PENDING")
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError("End date cannot be earlier than start date.")

    def __str__(self):
        return f"Leave request #{self.pk} — {self.student}"


class VisitorLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="visitors")
    visitor_name = models.CharField(max_length=120)
    visitor_phone = models.CharField(max_length=20, blank=True)
    purpose = models.CharField(max_length=200, blank=True)
    entry_time = models.DateTimeField(default=timezone.now)
    exit_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.visitor_name} visiting {self.student}"


class MealAttendance(models.Model):
    MEALS = [("BREAKFAST", "Breakfast"), ("LUNCH", "Lunch"), ("DINNER", "Dinner")]
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="meal_attendance")
    date = models.DateField(default=timezone.localdate)
    meal = models.CharField(max_length=10, choices=MEALS)
    present = models.BooleanField(default=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["student", "date", "meal"], name="unique_student_meal_date")]

    def __str__(self):
        return f"{self.student} — {self.date} — {self.meal}"


class Notice(models.Model):
    title = models.CharField(max_length=160)
    message = models.TextField()
    published = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class AuditEvent(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=100)
    object_type = models.CharField(max_length=100)
    object_id = models.CharField(max_length=50, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.timestamp}: {self.action} ({self.object_type})"
