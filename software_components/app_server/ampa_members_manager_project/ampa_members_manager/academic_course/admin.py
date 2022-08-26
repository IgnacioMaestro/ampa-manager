from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.academic_course.models.active_course import ActiveCourse


class AcademicCourseAdmin(admin.ModelAdmin):
    list_display = ['summary', 'fee', 'is_active', 'members_count']

    @staticmethod
    def summary(instance):
        return str(instance)
    
    @admin.display(description=_('Is active'))
    def is_active(self, academic_course):
        return _('Yes') if ActiveCourse.load().initial_year == academic_course.initial_year else _('No')
    
    @admin.display(description=_('Members'))
    def members_count(self, academic_course):
        return academic_course.membership_set.count()
