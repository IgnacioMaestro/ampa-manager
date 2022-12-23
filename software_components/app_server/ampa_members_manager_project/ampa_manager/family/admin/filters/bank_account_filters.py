from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ampa_manager.family.models.state import State


class BankAccountAuthorizationFilter(admin.SimpleListFilter):
    title = _('Authorization')

    parameter_name = 'authorization'

    def lookups(self, request, model_admin):
        return (
            (0, _('No authorization')),
            (State.NOT_SENT, _('Created')),
            (State.SENT, _('Sent')),
            (State.SIGNED, _('Signed')),
        )

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == '0':
                return queryset.without_authorization()
            else:
                return queryset.with_authorization_state(self.value())
        else:
            return queryset


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
