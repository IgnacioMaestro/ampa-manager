from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.academic_course.models.level import Level


class RegistrationFilter(admin.SimpleListFilter):
    title = _('Membership')

    parameter_name = 'member'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Members')),
            ('no', _('No members')),
        )

    def queryset(self, request, queryset):
        if self.value():
            course: AcademicCourse = ActiveCourse.load()
            if self.value() == 'yes':
                return queryset.members_in_course(course)
            elif self.value() == 'no':
                return queryset.no_members_in_course(course)
        else:
            return queryset


class ChildLevelListFilter(admin.SimpleListFilter):
    title = _('Course')

    parameter_name = 'course'

    def lookups(self, request, model_admin):
        return (
            (Level.AGE_HH2, Level.NAME_HH2),
            (Level.AGE_HH3, Level.NAME_HH3),
            (Level.AGE_HH4, Level.NAME_HH4),
            (Level.AGE_HH5, Level.NAME_HH5),
            (Level.AGE_LH1, Level.NAME_LH1),
            (Level.AGE_LH2, Level.NAME_LH2),
            (Level.AGE_LH3, Level.NAME_LH3),
            (Level.AGE_LH4, Level.NAME_LH4),
            (Level.AGE_LH5, Level.NAME_LH5),
            (Level.AGE_LH6, Level.NAME_LH6),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.child_of_age(int(self.value()))
        else:
            return queryset


class FamilyRegistrationFilter(admin.SimpleListFilter):
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
