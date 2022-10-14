from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.family.models.family import Family


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
            active_course = ActiveCourse.load()

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
                return queryset.with_default_account()
            elif self.value() == 'without':
                return queryset.without_default_account()
        else:
            return queryset
