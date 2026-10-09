from django.http import JsonResponse
from django.shortcuts import render
from .models import Student, Room, Allocation, FeeInvoice, Complaint, LeaveRequest, Notice

def home(request):
    context = {
        "student_count": Student.objects.count(),
        "room_count": Room.objects.count(),
        "active_allocations": Allocation.objects.filter(checked_out_at__isnull=True).count(),
        "unpaid_invoices": FeeInvoice.objects.exclude(status="PAID").count(),
        "open_complaints": Complaint.objects.exclude(status="RESOLVED").count(),
        "pending_leave": LeaveRequest.objects.filter(status="PENDING").count(),
        "notices": Notice.objects.filter(published=True).order_by("-created_at")[:5],
    }
    return render(request, "hostel/home.html", context)

def health(request):
    return JsonResponse({"status": "ok", "application": "Hostel Management System"})
