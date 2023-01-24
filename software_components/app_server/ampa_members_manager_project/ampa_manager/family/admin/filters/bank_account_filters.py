from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class BankAccountBICCodeFilter(admin.SimpleListFilter):
    title = _('SWIFT/BIC')

    parameter_name = 'bic'

    def lookups(self, request, model_admin):
        return (
            ('with', _('With SWIFT/BIC')),
            ('without', _('Without SWIFT/BIC')),
        )

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == 'with':
                return queryset.with_swift_bic()
            elif self.value() == 'without':
                return queryset.without_swift_bic()
        else:
            return queryset
