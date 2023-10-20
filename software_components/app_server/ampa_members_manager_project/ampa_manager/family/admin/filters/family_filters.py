from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class FamilyIsMemberFilter(admin.SimpleListFilter):
    title = _('Membership')

    parameter_name = 'member'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
            ('last_year', _('Last year')),
        )

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == 'yes':
                return queryset.members()
            elif self.value() == 'no':
                return queryset.no_members()
            elif self.value() == 'last_year':
                return queryset.members_last_year()
        else:
            return queryset


class FamilyChildrenInSchoolFilter(admin.SimpleListFilter):
    title = _('Children in school')

    parameter_name = 'children_in_school'

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


class DefaultHolder(admin.SimpleListFilter):
    title = _('Default holder')

    parameter_name = 'default_holder'

    def lookups(self, request, model_admin):
        return (
            ('with', _('Completed')),
            ('without', _('Not completed')),
        )

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == 'with':
                return queryset.with_default_holder()
            elif self.value() == 'without':
                return queryset.without_default_holder()
        else:
            return queryset


class CustodyHolder(admin.SimpleListFilter):
    title = _('Custody holder')

    parameter_name = 'custody_holder'

    def lookups(self, request, model_admin):
        return (
            ('with', _('Completed')),
            ('without', _('Not completed')),
        )

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == 'with':
                return queryset.with_custody_holder()
            elif self.value() == 'without':
                return queryset.without_custody_holder()
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
