from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, GlobalSettings


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            None,
            {
                "fields": (
                    "role",
                    "telephone",
                )
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            None,
            {
                "fields": (
                    "role",
                    "telephone",
                )
            },
        ),
    )
    list_display = (
        "username",
        "telephone",
        "role",
        "solde",
        "platform_balance",
        "active",
    )
    list_filter = ("role", "active")
    actions = ["deactivate_fournisseurs", "activate_fournisseurs"]

    def deactivate_fournisseurs(self, request, queryset):
        queryset.update(active=False)

    deactivate_fournisseurs.short_description = (
        "Désactiver les fournisseurs sélectionnés"
    )

    def activate_fournisseurs(self, request, queryset):
        queryset.update(active=True)

    activate_fournisseurs.short_description = "Activer les fournisseurs sélectionnés"


admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ("commission_rate",)
