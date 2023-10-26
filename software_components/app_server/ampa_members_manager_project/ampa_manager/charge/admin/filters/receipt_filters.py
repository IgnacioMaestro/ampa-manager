from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class CampsReceiptFilter(admin.SimpleListFilter):
    title = _('Family')

    parameter_name = 'family'

    def lookups(self, request, model_admin):
        return (
            ('all', _('All')),
        )

    def queryset(self, request, queryset):
        if self.value() and self.value() != 'all':
            return queryset.of_family(self.value())
        else:
            return queryset

class CustodyReceiptFilter(admin.SimpleListFilter):
    title = _('Family')

    parameter_name = 'family'

    def lookups(self, request, model_admin):
        return (
            ('all', _('All')),
        )

    def queryset(self, request, queryset):
        if self.value() and self.value() != 'all':
            return queryset.of_family(self.value())
        else:
            return queryset

class AfterSchoolReceiptFilter(admin.SimpleListFilter):
    title = _('Family')

    parameter_name = 'family'

    def lookups(self, request, model_admin):
        return (
            ('all', _('All')),
        )

    def queryset(self, request, queryset):
        if self.value() and self.value() != 'all':
            return queryset.of_family(self.value())
        else:
            return queryset
