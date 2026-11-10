
from django.apps import AppConfig


class HostelConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hostel"

    def ready(self):
        from .signals import register_audit_signals
        register_audit_signals()
