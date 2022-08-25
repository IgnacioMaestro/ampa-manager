from datetime import date

from django.db.models import Q
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.academic_course.models.academic_course import AcademicCourse


class CourseListFilter(admin.SimpleListFilter):
    title = _('Course')

    parameter_name = 'course'

    def lookups(self, request, model_admin):
        return (
            ('HH2', _('HH2')),
            ('HH3', _('HH3')),
            ('HH4', _('HH4')),
            ('HH5', _('HH5')),
            ('LH1', _('LH1')),
            ('LH2', _('LH2')),
            ('LH3', _('LH3')),
            ('LH4', _('LH4')),
            ('LH5', _('LH5')),
            ('LH6', _('LH6')),
        )

    def queryset(self, request, queryset):
        if self.value():
            selected_course = self.value()
            years_since_birth = AcademicCourse.get_default_years_since_birth(selected_course)
            active_course = ActiveCourse.load()
            default_year_of_birth = active_course.initial_year - years_since_birth

            return queryset.filter(Q(year_of_birth=default_year_of_birth, repetition=0) |
                                   Q(year_of_birth=default_year_of_birth - 1, repetition=1) |
                                   Q(year_of_birth=default_year_of_birth - 2, repetition=2) |
                                   Q(year_of_birth=default_year_of_birth - 3, repetition=3))
        else:
            return queryset

class AuthorizationListFilter(admin.SimpleListFilter):
    title = _('No d')

    parameter_name = 'course'

    def lookups(self, request, model_admin):
        return (
            ('HH2', _('HH2')),
            ('HH3', _('HH3')),
            ('HH4', _('HH4')),
            ('HH5', _('HH5')),
            ('LH1', _('LH1')),
            ('LH2', _('LH2')),
            ('LH3', _('LH3')),
            ('LH4', _('LH4')),
            ('LH5', _('LH5')),
            ('LH6', _('LH6')),
        )

    def queryset(self, request, queryset):
        if self.value():
            selected_course = self.value()
            years_since_birth = AcademicCourse.get_default_years_since_birth(selected_course)
            active_course = ActiveCourse.load()
            default_year_of_birth = active_course.initial_year - years_since_birth

            return queryset.filter(Q(year_of_birth=default_year_of_birth, repetition=0) |
                                   Q(year_of_birth=default_year_of_birth - 1, repetition=1) |
                                   Q(year_of_birth=default_year_of_birth - 2, repetition=2) |
                                   Q(year_of_birth=default_year_of_birth - 3, repetition=3))
        else:
            return queryset
