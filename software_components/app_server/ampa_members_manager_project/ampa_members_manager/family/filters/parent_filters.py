from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.family.models.state import State


class ParentFamilyEmailsFilter(admin.SimpleListFilter):
    title = _('Family emails')

    parameter_name = 'family_email'

    def lookups(self, request, model_admin):
        return (
            ('with', _('With email')),
            ('without', _('Without email')),
        )

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == 'with':
                return queryset.with_email()
            elif self.value() == 'without':
                return queryset.without_email()
        else:
            return queryset


class ParentFamiliesCountFilter(admin.SimpleListFilter):
    title = _('Families count')

    parameter_name = 'families_count'

    def lookups(self, request, model_admin):
        return (
            ('0', _('No families')),
            ('1', _('One family')),
            ('2+', _('More than one family')),
        )

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == '0':
                return queryset.has_no_family()
            elif self.value() == '1':
                return queryset.has_one_family()
            elif self.value() == '2+':
                return queryset.has_multiple_families()
        else:
            return queryset
