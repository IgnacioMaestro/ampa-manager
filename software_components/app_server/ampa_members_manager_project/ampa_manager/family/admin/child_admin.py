from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ampa_manager.academic_course.models.level import Level
from ampa_manager.activity.admin_to_divide import AfterSchoolRegistrationInline
from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.family.admin.filters.child_filters import ChildCycleFilter, ChildLevelListFilter
from ampa_manager.family.models.membership import Membership


class ChildAdmin(admin.ModelAdmin):
    list_display = ['name', 'family', 'parents', 'after_schools_count', 'year_of_birth', 'child_course', 'is_member']
    fields = ['name', 'family', 'year_of_birth', 'repetition', 'created', 'modified']
    readonly_fields = ['created', 'modified']
    ordering = ['name']
    list_filter = [ChildCycleFilter, ChildLevelListFilter, 'year_of_birth', 'repetition']
    search_fields = ['name', 'year_of_birth', 'family__surnames']
    list_per_page = 25
    inlines = [AfterSchoolRegistrationInline]

    @admin.display(description=_('Is member'))
    def is_member(self, child):
        return _('Yes') if Membership.is_member_child(child) else _('No')

    @admin.display(description=_('Course'))
    def child_course(self, child):
        return Level.get_level_name(child.level)

    @admin.display(description=_('Parents'))
    def parents(self, child):
        return ', '.join(p.name_and_surnames for p in child.family.parents.all())

    @admin.display(description=_('After-schools'))
    def after_schools_count(self, child):
        return AfterSchoolRegistration.objects.of_child(child).count()
