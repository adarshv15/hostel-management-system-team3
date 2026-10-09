from django.contrib import admin
from django.db.models import Sum, Value, DecimalField
from django.db.models.functions import Coalesce

from .models import (
    Student,
    Room,
    Allocation,
    FeeInvoice,
    PaymentRecord,
    Complaint,
    LeaveRequest,
    VisitorLog,
    MealAttendance,
    Notice,
    AuditEvent,
)


class AuditLoggingAdmin(admin.ModelAdmin):
    """
    Automatically logs create, update, and delete actions
    performed through the Django admin panel.
    """

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        AuditEvent.objects.create(
            actor=request.user,
            action="UPDATE" if change else "CREATE",
            object_type=obj.__class__.__name__,
            object_id=str(obj.pk),
            details={
                "message": (
                    f"{obj.__class__.__name__} "
                    f"{'updated' if change else 'created'} "
                    "through Django admin."
                )
            },
        )

    def delete_model(self, request, obj):
        AuditEvent.objects.create(
            actor=request.user,
            action="DELETE",
            object_type=obj.__class__.__name__,
            object_id=str(obj.pk),
            details={
                "message": (
                    f"{obj.__class__.__name__} "
                    "deleted through Django admin."
                )
            },
        )

        super().delete_model(request, obj)


@admin.register(Student)
class StudentAdmin(AuditLoggingAdmin):
    list_display = (
        "student_id",
        "full_name",
        "email",
        "status",
        "course",
    )
    list_filter = ("status", "course")
    search_fields = ("student_id", "full_name", "email")
    ordering = ("student_id",)


@admin.register(Room)
class RoomAdmin(AuditLoggingAdmin):
    list_display = (
        "block",
        "room_number",
        "room_type",
        "capacity",
        "occupied_beds",
        "available_beds",
        "is_active",
    )
    list_filter = ("block", "room_type", "is_active")
    search_fields = ("room_number", "block")


@admin.register(Allocation)
class AllocationAdmin(AuditLoggingAdmin):
    list_display = (
        "student",
        "room",
        "bed_label",
        "allocated_at",
        "checked_out_at",
    )
    list_filter = ("room__block",)
    search_fields = (
        "student__full_name",
        "student__student_id",
        "room__room_number",
    )


@admin.register(FeeInvoice)
class FeeInvoiceAdmin(AuditLoggingAdmin):
    list_display = (
        "id",
        "student",
        "description",
        "amount",
        "total_paid",
        "balance_due",
        "due_date",
        "status",
    )

    list_filter = ("status", "due_date")
    search_fields = (
        "student__full_name",
        "student__student_id",
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        money_field = DecimalField(
            max_digits=12,
            decimal_places=2,
        )

        return queryset.annotate(
            _total_paid=Coalesce(
                Sum("payments__amount"),
                Value(0, output_field=money_field),
                output_field=money_field,
            )
        )

    @admin.display(description="Total Paid")
    def total_paid(self, obj):
        return obj._total_paid or 0

    @admin.display(description="Balance Due")
    def balance_due(self, obj):
        total_paid = obj._total_paid or 0
        return max(obj.amount - total_paid, 0)


@admin.register(PaymentRecord)
class PaymentRecordAdmin(AuditLoggingAdmin):
    list_display = (
        "invoice",
        "amount",
        "mode",
        "reference",
        "recorded_by",
        "recorded_at",
    )
    list_filter = ("mode", "recorded_at")
    search_fields = (
        "reference",
        "invoice__student__full_name",
        "invoice__student__student_id",
    )


@admin.register(Complaint)
class ComplaintAdmin(AuditLoggingAdmin):
    list_display = (
        "id",
        "student",
        "category",
        "status",
        "assigned_to",
        "created_at",
    )
    list_filter = ("status", "category")
    search_fields = (
        "student__full_name",
        "description",
    )
    list_editable = ("status", "assigned_to")


@admin.register(LeaveRequest)
class LeaveRequestAdmin(AuditLoggingAdmin):
    list_display = (
        "student",
        "start_date",
        "end_date",
        "status",
        "reviewed_by",
    )
    list_filter = ("status",)
    list_editable = ("status",)


@admin.register(VisitorLog)
class VisitorLogAdmin(AuditLoggingAdmin):
    list_display = (
        "visitor_name",
        "student",
        "entry_time",
        "exit_time",
    )
    search_fields = (
        "visitor_name",
        "student__full_name",
        "student__student_id",
    )


@admin.register(MealAttendance)
class MealAttendanceAdmin(AuditLoggingAdmin):
    list_display = (
        "student",
        "date",
        "meal",
        "present",
    )
    list_filter = ("date", "meal", "present")
    search_fields = (
        "student__full_name",
        "student__student_id",
    )


@admin.register(Notice)
class NoticeAdmin(AuditLoggingAdmin):
    list_display = (
        "title",
        "published",
        "created_by",
        "created_at",
    )
    list_filter = ("published", "created_at")
    search_fields = ("title", "message")


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = (
        "timestamp",
        "actor",
        "action",
        "object_type",
        "object_id",
    )
    list_filter = ("action", "object_type")
    search_fields = (
        "action",
        "object_type",
        "object_id",
    )
    readonly_fields = (
        "actor",
        "action",
        "object_type",
        "object_id",
        "timestamp",
        "details",
    )
    ordering = ("-timestamp",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
