from typing import Optional

from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse


class FamilyIsMemberFilter(admin.SimpleListFilter):
    title = _('Membership')

    parameter_name = 'member'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Current year members')),
            ('no', _('Current year NO members')),
            ('last_year', _('Last year members')),
            ('renew', _('Renew (Last year + Children + Renew)')),
            ('no_renew', _('Out of school (Last year + No children)')),
        )

    def queryset(self, request, queryset):
        if self.value():
            course: AcademicCourse = ActiveCourse.load()
            previous_course: Optional[AcademicCourse] = ActiveCourse.get_previous()
            if self.value() == 'yes':
                return queryset.members_in_course(course)
            elif self.value() == 'no':
                return queryset.no_members_in_course(course)
            elif self.value() == 'last_year':
                return queryset.members_in_course(previous_course)
            elif self.value() == 'renew':
                messages.success(request, _('Showing families that were members last year, that have any child in the school this year and that have not decline membership'))
                return queryset.members_in_course(previous_course).no_declined_membership().has_any_children()
            elif self.value() == 'no_renew':
                messages.success(request, _('Showing families that were members last year, but they haven\'t any child in the school'))
                return queryset.members_in_course(previous_course).has_no_children()
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


class FamilyDuplicated(admin.SimpleListFilter):
    title = _('Possible duplicated')

    parameter_name = 'duplicated'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == 'yes':
                return queryset.possible_duplicated()
        else:
            return queryset


class MembershipHolder(admin.SimpleListFilter):
    title = _('Membership holder')

    parameter_name = 'membership_holder'

    def lookups(self, request, model_admin):
        return (
            ('with', _('Completed')),
            ('without', _('Not completed')),
        )

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == 'with':
                return queryset.with_membership_holder()
            elif self.value() == 'without':
                return queryset.without_membership_holder()
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


class CampsHolder(admin.SimpleListFilter):
    title = _('Camps holder')

    parameter_name = 'camps_holder'

    def lookups(self, request, model_admin):
        return (
            ('with', _('Completed')),
            ('without', _('Not completed')),
        )

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == 'with':
                return queryset.with_camps_holder()
            elif self.value() == 'without':
                return queryset.without_camps_holder()
        else:
            return queryset


class AfterSchoolHolder(admin.SimpleListFilter):
    title = _('After-school holder')

    parameter_name = 'after_school_holder'

    def lookups(self, request, model_admin):
        return (
            ('with', _('Completed')),
            ('without', _('Not completed')),
        )

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == 'with':
                return queryset.with_after_school_holder()
            elif self.value() == 'without':
                return queryset.without_after_school_holder()
        else:
            return queryset


class AnyHolder(admin.SimpleListFilter):
    title = _('Any holder')

    parameter_name = 'any_holder'

    def lookups(self, request, model_admin):
        return (
            ('missing', _('Any missing')),
            ('completed', _('All completed')),
        )

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == 'missing':
                return queryset.any_holder_missing()
            elif self.value() == 'completed':
                return queryset.all_holders_completed()
        else:
            return queryset


class FamilyEmail(admin.SimpleListFilter):
    title = _('Email')

    parameter_name = 'email'

    def lookups(self, request, model_admin):
        return (
            ('missing', _('Missing')),
            ('completed', _('Completed')),
        )

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == 'missing':
                return queryset.without_email()
            elif self.value() == 'completed':
                return queryset.with_email()
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
