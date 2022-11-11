from django.contrib import admin
from django.db.models import F
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.academic_course.models.level import Level


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
            return queryset.of_age(int(self.value()))
        else:
            return queryset
