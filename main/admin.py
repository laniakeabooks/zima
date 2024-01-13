from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjUserAdmin

from main import models

admin.site.site_header = "01z.co admin"


@admin.register(models.User)
class UserAdmin(DjUserAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "date_joined",
        "last_login",
    )
    list_display_links = ("id", "username")

    fieldsets = (
        (None, {"fields": ("username", "password", "email")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    search_fields = ("username", "email")

    ordering = ["-id"]


@admin.register(models.Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "contact",
        "resource",
    )
    search_fields = ("contact", "resource")
