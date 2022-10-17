from django.db.models import F
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.academic_course.models.course_name import CourseName


class ChildCourseListFilter(admin.SimpleListFilter):
    title = _('Course')

    parameter_name = 'course'

    def lookups(self, request, model_admin):
        return (
            (CourseName.AGE_HH2, CourseName.LABEL_HH2),
            (CourseName.AGE_HH3, CourseName.LABEL_HH3),
            (CourseName.AGE_HH4, CourseName.LABEL_HH4),
            (CourseName.AGE_HH5, CourseName.LABEL_HH5),
            (CourseName.AGE_LH1, CourseName.LABEL_LH1),
            (CourseName.AGE_LH2, CourseName.LABEL_LH3),
            (CourseName.AGE_LH3, CourseName.LABEL_LH4),
            (CourseName.AGE_LH4, CourseName.LABEL_LH4),
            (CourseName.AGE_LH5, CourseName.LABEL_LH5),
            (CourseName.AGE_LH6, CourseName.LABEL_LH6),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.by_age(int(self.value()))
        else:
            return queryset

class ChildCycleFilter(admin.SimpleListFilter):
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
                return queryset.in_pre_school()
            elif self.value() == 'pri':
                return queryset.in_primary()
            elif self.value() == 'out':
                return queryset.out_of_school()
        else:
            return queryset
