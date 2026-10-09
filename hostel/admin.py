from django.contrib import admin
from .models import (
    Student, Room, Allocation, FeeInvoice, PaymentRecord, Complaint,
    LeaveRequest, VisitorLog, MealAttendance, Notice, AuditEvent
)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_id", "full_name", "email", "status", "course")
    list_filter = ("status", "course")
    search_fields = ("student_id", "full_name", "email")
    ordering = ("student_id",)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("block", "room_number", "room_type", "capacity", "occupied_beds", "available_beds", "is_active")
    list_filter = ("block", "room_type", "is_active")
    search_fields = ("room_number", "block")

@admin.register(Allocation)
class AllocationAdmin(admin.ModelAdmin):
    list_display = ("student", "room", "bed_label", "allocated_at", "checked_out_at")
    list_filter = ("room__block",)
    search_fields = ("student__full_name", "student__student_id", "room__room_number")

@admin.register(FeeInvoice)
class FeeInvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "description", "amount", "due_date", "status")
    list_filter = ("status", "due_date")
    search_fields = ("student__full_name", "student__student_id")

@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ("invoice", "amount", "mode", "reference", "recorded_by", "recorded_at")
    list_filter = ("mode", "recorded_at")

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "category", "status", "assigned_to", "created_at")
    list_filter = ("status", "category")
    search_fields = ("student__full_name", "description")
    list_editable = ("status", "assigned_to")

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ("student", "start_date", "end_date", "status", "reviewed_by")
    list_filter = ("status",)
    list_editable = ("status",)

@admin.register(VisitorLog)
class VisitorLogAdmin(admin.ModelAdmin):
    list_display = ("visitor_name", "student", "entry_time", "exit_time")
    search_fields = ("visitor_name", "student__full_name")

@admin.register(MealAttendance)
class MealAttendanceAdmin(admin.ModelAdmin):
    list_display = ("student", "date", "meal", "present")
    list_filter = ("date", "meal", "present")

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ("title", "published", "created_by", "created_at")
    list_filter = ("published", "created_at")
    search_fields = ("title", "message")

@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "actor", "action", "object_type", "object_id")
    list_filter = ("action", "object_type")
    readonly_fields = ("actor", "action", "object_type", "object_id", "timestamp", "details")
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
