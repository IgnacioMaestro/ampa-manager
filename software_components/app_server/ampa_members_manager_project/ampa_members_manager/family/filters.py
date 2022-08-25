from datetime import date

from django.db.models import Q, F
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.academic_course.models.academic_course import AcademicCourse
from ampa_members_manager.academic_course.models.course_name import CourseName


class CourseListFilter(admin.SimpleListFilter):
    title = _('Course')

    parameter_name = 'course'

    def lookups(self, request, model_admin):
        return (
            (2, _('HH2')),
            (3, _('HH3')),
            (4, _('HH4')),
            (5, _('HH5')),
            (6, _('LH1')),
            (7, _('LH2')),
            (8, _('LH3')),
            (9, _('LH4')),
            (10, _('LH5')),
            (11, _('LH6')),
        )

    def queryset(self, request, queryset):
        if self.value():
            years_since_birth = int(self.value())
            active_course = ActiveCourse.load()
            default_year_of_birth = active_course.initial_year - years_since_birth

            return queryset.filter(Q(year_of_birth=default_year_of_birth - F('repetition')))
        else:
            return queryset
