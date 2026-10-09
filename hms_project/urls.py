from django.contrib import admin
from django.urls import path
from hostel.views import home, health

urlpatterns = [
    path("", home, name="home"),
    path("health/", health, name="health"),
    path("admin/", admin.site.urls),
]
