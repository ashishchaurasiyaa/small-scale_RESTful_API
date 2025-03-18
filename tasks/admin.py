from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "assigned_to", "created_at", "updated_at")
    list_filter = ("status", "assigned_to")
    search_fields = ("title", "description")
    list_per_page = 20
    ordering = ("-created_at",)

    fieldsets = (
        (None, {
            "fields": ("title", "description", "status"),
        }),
        ("Assignment", {
            "fields": ("assigned_to",),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    readonly_fields = ("created_at", "updated_at")