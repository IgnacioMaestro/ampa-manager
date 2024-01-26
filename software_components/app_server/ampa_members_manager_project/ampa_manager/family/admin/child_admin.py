from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ampa_manager.academic_course.models.level import Level
from ampa_manager.activity.admin.after_school_admin import AfterSchoolRegistrationInline
from ampa_manager.activity.admin.camps_admin import CampsRegistrationInline
from ampa_manager.activity.admin.custody_admin import CustodyRegistrationInline
from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.activity.models.camps.camps_registration import CampsRegistration
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.family.admin.filters.child_filters import ChildCycleFilter, ChildLevelListFilter
from ampa_manager.family.models.membership import Membership


class ChildAdmin(admin.ModelAdmin):
    list_display = ['name', 'family', 'after_school_registrations', 'custody_registrations',
                    'camps_registrations', 'year_of_birth', 'child_course', 'is_member']
    fields = ['name', 'family', 'parents', 'year_of_birth', 'repetition', 'created', 'modified']
    readonly_fields = ['created', 'modified', 'parents']
    ordering = ['name']
    list_filter = [ChildCycleFilter, ChildLevelListFilter, 'year_of_birth', 'repetition']
    search_fields = ['name', 'year_of_birth', 'family__surnames', 'id']
    list_per_page = 25
    inlines = [AfterSchoolRegistrationInline, CustodyRegistrationInline, CampsRegistrationInline]

    @admin.display(description=_('Is member'))
    def is_member(self, child):
        return _('Yes') if Membership.is_member_child(child) else _('No')

    @admin.display(description=_('Course'))
    def child_course(self, child):
        return Level.get_level_name(child.level)

    @admin.display(description=_('Parents'))
    def parents(self, child):
        return ', '.join(p.name_and_surnames for p in child.family.parents.all())

    @admin.display(description=_('After-sch.'))
    def after_school_registrations(self, child):
        active_course = AfterSchoolRegistration.objects.of_child(child).of_active_course().count()
        previous_courses = AfterSchoolRegistration.objects.of_child(child).of_previous_courses().count()
        return f'{active_course} / {previous_courses}'

    @admin.display(description=_('Cust.'))
    def custody_registrations(self, child):
        active_course = CustodyRegistration.objects.of_child(child).of_active_course().count()
        previous_courses = CustodyRegistration.objects.of_child(child).of_previous_courses().count()
        return f'{active_course} / {previous_courses}'

    @admin.display(description=_('Cmps.'))
    def camps_registrations(self, child):
        active_course = CampsRegistration.objects.of_child(child).of_active_course().count()
        previous_courses = CampsRegistration.objects.of_child(child).of_previous_courses().count()
        return f'{active_course} / {previous_courses}'

    @admin.display(description=_('Parents'))
    def parents(self, child):
        return ', '.join([str(p) for p in child.family.parents.all()])
