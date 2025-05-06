from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class FamilyReceiptFilter(admin.SimpleListFilter):
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


class ParentReceiptFilter(admin.SimpleListFilter):
    title = _('Parent')

    parameter_name = 'parent'

    def lookups(self, request, model_admin):
        return (
            ('all', _('All')),
        )

    def queryset(self, request, queryset):
        if self.value() and self.value() != 'all':
            return queryset.of_parent(self.value())
        else:
            return queryset


class AfterSchoolEditionReceiptFilter(admin.SimpleListFilter):
    title = _('Edition')

    parameter_name = 'edition'

    def lookups(self, request, model_admin):
        return (
            ('all', _('All')),
        )

    def queryset(self, request, queryset):
        if self.value() and self.value() != 'all':
            return queryset.of_edition(self.value())
        else:
            return queryset
