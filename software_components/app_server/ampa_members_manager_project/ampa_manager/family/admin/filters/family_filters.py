from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ampa_manager.family.models.family import Family


class FamilyIsMemberFilter(admin.SimpleListFilter):
    title = _('Membership')

    parameter_name = 'member'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Members')),
            ('no', _('No members')),
        )

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == 'yes':
                return Family.objects.members()
            elif self.value() == 'no':
                return Family.objects.no_members()
        else:
            return queryset


class FamilyChildrenCountFilter(admin.SimpleListFilter):
    title = _('Children count')

    parameter_name = 'children'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Any children in school')),
            ('no', _('No children in school')),
        )

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == 'yes':
                return queryset.has_any_children()
            elif self.value() == 'no':
                return queryset.has_no_children()
        else:
            return queryset


class FamilyDefaultAccountFilter(admin.SimpleListFilter):
    title = _('Default account')

    parameter_name = 'account'

    def lookups(self, request, model_admin):
        return (
            ('with', _('With account')),
            ('without', _('Without account')),
        )

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == 'with':
                return queryset.with_default_bank_account()
            elif self.value() == 'without':
                return queryset.without_default_bank_account()
        else:
            return queryset


class FamilyParentCountFilter(admin.SimpleListFilter):
    title = _('Numer of parents')

    parameter_name = 'parents'

    def lookups(self, request, model_admin):
        return (
            ('0', _('No parents')),
            ('1', _('1 parent')),
            ('2', _('2 parent')),
            ('3+', _('More than 2 parents')),
        )

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == '0':
                return queryset.with_number_of_parents(0)
            elif self.value() == '1':
                return queryset.with_number_of_parents(1)
            if self.value() == '2':
                return queryset.with_number_of_parents(2)
            elif self.value() == '3+':
                return queryset.with_more_than_two_parents()
        else:
            return queryset
