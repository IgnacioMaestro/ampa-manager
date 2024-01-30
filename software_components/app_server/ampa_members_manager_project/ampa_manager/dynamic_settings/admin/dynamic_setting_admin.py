from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class DynamicSettingAdmin(admin.ModelAdmin):
    list_display = ['remittances_party_id', 'remittances_generic_org_id', 'remittances_bic', 'remittances_iban']
    fieldsets = (
        (_('Remittances'), {
            'fields': ['remittances_party_id', 'remittances_generic_org_id', 'remittances_bic', 'remittances_iban']
        }),
        (_('Custody'), {
            'fields': ['custody_members_discount_percent', 'custody_max_days_to_charge_percent'],
        }),
        # (_('After-school'), {
        #     'fields': [],
        # }),
        # (_('Camps'), {
        #     'fields': [],
        # }),
        # (_('Members'), {
        #     'fields': [],
        # }),
    )
    readonly_fields = []
