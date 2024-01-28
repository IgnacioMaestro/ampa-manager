from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class DynamicSettingAdmin(admin.ModelAdmin):
    list_display = []
    fieldsets = (
        (None, {
            'fields': ('ampa_iban',)
        }),
        (_('Custody'), {
            'fields': ('custody_members_discount_percent', 'custody_max_days_to_charge_per_month_percent'),
        }),
        (_('After-school'), {
            'fields': (),
        }),
        (_('Camps'), {
            'fields': (),
        }),
        (_('Members'), {
            'fields': (),
        }),
    )
    readonly_fields = []
