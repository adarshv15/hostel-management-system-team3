
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

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


# Models whose create, update, and delete actions should be logged.
TRACKED_MODELS = (
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
)


def create_audit_event(instance, action):
    """
    Create an audit event for a hostel model change.
    The actor is left empty because model signals do not
    automatically provide the user who performed the action.
    """
    if isinstance(instance, AuditEvent):
        return

    AuditEvent.objects.create(
        actor=None,
        action=action,
        object_type=instance.__class__.__name__,
        object_id=str(instance.pk) if instance.pk is not None else "",
        details={
            "message": (
                f"{instance.__class__.__name__} "
                f"{action.lower()} event."
            )
        },
    )


def audit_post_save(sender, instance, created, **kwargs):
    """Log when a tracked object is created or updated."""
    action = "CREATE" if created else "UPDATE"
    create_audit_event(instance, action)


def audit_post_delete(sender, instance, **kwargs):
    """Log when a tracked object is deleted."""
    create_audit_event(instance, "DELETE")


def register_audit_signals():
    """Register audit handlers for all tracked hostel models."""

    for model in TRACKED_MODELS:
        post_save.connect(
            audit_post_save,
            sender=model,
            weak=False,
            dispatch_uid=f"hostel_audit_save_{model.__name__}",
        )

        post_delete.connect(
            audit_post_delete,
            sender=model,
            weak=False,
            dispatch_uid=f"hostel_audit_delete_{model.__name__}",
        )
