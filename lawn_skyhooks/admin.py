"""Admin site."""

# Django
# Register your models for the admin site here.
from django.contrib import admin

from .models import Skyhook


@admin.register(Skyhook)
class SkyhookAdmin(admin.ModelAdmin):
    list_display = [
        "location",
        "resource_type",
        "resource_per_minute",
        "last_emptied_at",
    ]
