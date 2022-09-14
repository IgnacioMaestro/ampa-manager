from datetime import date

from django.db.models import Q, F
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.academic_course.models.academic_course import AcademicCourse


class CourseListFilter(admin.SimpleListFilter):
    title = _('Course')

    parameter_name = 'course'

    def lookups(self, request, model_admin):
        return (
            (AcademicCourse.HH2_YEARS_SINCE_BIRTH, _('HH2')),
            (AcademicCourse.HH3_YEARS_SINCE_BIRTH, _('HH3')),
            (AcademicCourse.HH4_YEARS_SINCE_BIRTH, _('HH4')),
            (AcademicCourse.HH5_YEARS_SINCE_BIRTH, _('HH5')),
            (AcademicCourse.LH1_YEARS_SINCE_BIRTH, _('LH1')),
            (AcademicCourse.LH2_YEARS_SINCE_BIRTH, _('LH2')),
            (AcademicCourse.LH3_YEARS_SINCE_BIRTH, _('LH3')),
            (AcademicCourse.LH4_YEARS_SINCE_BIRTH, _('LH4')),
            (AcademicCourse.LH5_YEARS_SINCE_BIRTH, _('LH5')),
            (AcademicCourse.LH6_YEARS_SINCE_BIRTH, _('LH6')),
        )

    def queryset(self, request, queryset):
        if self.value():
            years_since_birth = int(self.value())
            active_course = ActiveCourse.load()
            default_year_of_birth = active_course.initial_year - years_since_birth

            return queryset.annotate(course=active_course.initial_year - F('year_of_birth') - F('repetition')).filter(course=years_since_birth)
        else:
            return queryset

class CycleFilter(admin.SimpleListFilter):
    title = _('Cycle')

    parameter_name = 'cycle'

    def lookups(self, request, model_admin):
        return (
            ('pre', _('Pre-school')),
            ('pri', _('Primary education')),
            ('out', _('Out of school')),
        )

    def queryset(self, request, queryset):
        if self.value():
            active_course = ActiveCourse.load()

            queryset = queryset.annotate(course=active_course.initial_year - F('year_of_birth') - F('repetition'))

            if self.value() == 'pre':
                return queryset.filter(course__range=(AcademicCourse.HH2_YEARS_SINCE_BIRTH, AcademicCourse.HH5_YEARS_SINCE_BIRTH))
            elif self.value() == 'pri':
                return queryset.filter(course__range=(AcademicCourse.LH1_YEARS_SINCE_BIRTH, AcademicCourse.LH6_YEARS_SINCE_BIRTH))
            elif self.value() == 'out':
                return queryset.filter(Q(course__lt=AcademicCourse.HH2_YEARS_SINCE_BIRTH) | Q(course__gt=AcademicCourse.LH6_YEARS_SINCE_BIRTH))
        else:
            return queryset
