from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.academic_course.models.active_course import ActiveCourse


class AcademicCourseAdmin(admin.ModelAdmin):
    list_display = ['summary', 'fee', 'is_active']

    @staticmethod
    def summary(instance):
        return str(instance)
    
    @admin.display(description=_('Is active'))
    def is_active(self, academic_course):
        return ActiveCourse.load().initial_year == academic_course.initial_year
        return child.family.membership_set.filter(academic_course=ActiveCourse.load()).exists()
