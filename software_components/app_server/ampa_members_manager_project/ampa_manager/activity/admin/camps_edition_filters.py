from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.camps.camps_edition import CampsEdition


class CampsEditionHasRemittanceFilter(admin.SimpleListFilter):
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
                return CampsEdition.objects.with_remittance()
            elif self.value() == 'no':
                return CampsEdition.objects.without_remittance()
        else:
            return queryset
