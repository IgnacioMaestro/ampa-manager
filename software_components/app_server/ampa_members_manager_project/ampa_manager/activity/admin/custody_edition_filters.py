from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition


class CustodyEditionHasRemittanceFilter(admin.SimpleListFilter):
    title = _('Remittance')

    parameter_name = 'remittance'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Has remittance')),
            ('no', _('No remittance')),
        )

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == 'yes':
                return CustodyEdition.objects.with_remittance()
            elif self.value() == 'no':
                return CustodyEdition.objects.without_remittance()
        else:
            return queryset
