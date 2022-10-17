import imp
from traceback import format_exc
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.family.models.membership import Membership
from ampa_members_manager.family.models.parent import Parent
from ampa_members_manager.family.models.child import Child
from ampa_members_manager.academic_course.models.level import Level
from ampa_members_manager.family.models.family import Family


class AcademicCourseAdmin(admin.ModelAdmin):
    list_display = ['summary', 'fee', 'is_active', 'members_count']
    ordering = ['-id']
    list_per_page = 25

    @admin.display(description=_('Summary'))
    def summary(self, instance):
        return str(instance)
    
    @admin.display(description=_('Is active'))
    def is_active(self, academic_course):
        return _('Yes') if ActiveCourse.load().initial_year == academic_course.initial_year else _('No')
    
    @admin.display(description=_('Members'))
    def members_count(self, academic_course):
        return academic_course.membership_set.count()

class ActiveCourseAdmin(admin.ModelAdmin):
    list_display = ['course', 'members_count', 'families_in_school_count', 'parents_count', 'children_in_school_count']
    readonly_fields = ['members_count', 'families_in_school_count', 'parents_count', 'children_in_school_count', 'children_in_pre_school_count', 'children_in_primary_count', 'hh_members', 'hh2_members', 'hh3_members', 'hh4_members', 'hh5_members', 'lh_members', 'lh1_members', 'lh2_members', 'lh3_members', 'lh4_members', 'lh5_members', 'lh6_members']
    fieldsets = (
        (None, {
            'fields': ('course',)
        }),
        (_('Global'), {
            'fields': ('members_count', 'families_in_school_count', 'parents_count'),
        }),
        (_('Children'), {
            'fields': ('children_in_school_count', 'children_in_pre_school_count', 'children_in_primary_count'),
        }),
        (_('HH members'), {
            'fields': ('hh_members', 'hh2_members', 'hh3_members', 'hh4_members', 'hh5_members'),
        }),
        (_('LH members'), {
            'fields': ('lh_members', 'lh1_members', 'lh2_members', 'lh3_members', 'lh4_members', 'lh5_members', 'lh6_members'),
        }),
    )

    @admin.display(description=_('Members'))
    def members_count(self, active_course):
        return Membership.objects.active_course_members().count()
    
    @admin.display(description=_('Families'))
    def families_count(self, active_course):
        return Family.objects.count()
    
    @admin.display(description=_('Families with children in school'))
    def families_in_school_count(self, active_course):
        family_count = Family.objects.count()
        family_in_school_count = Family.objects.has_any_children().count()
        return f'{family_in_school_count}/{family_count}'
    
    @admin.display(description=_('Parents'))
    def parents_count(self, active_course):
        return Parent.objects.count()
    
    @admin.display(description=_('Children in school'))
    def children_in_school_count(self, active_course):
        children_count = Child.objects.count()
        children_in_school_count = Child.objects.in_school().count()
        return f'{children_in_school_count}/{children_count}'

    @admin.display(description=_('Pre-school'))
    def children_in_pre_school_count(self, active_course):
        return Child.objects.in_pre_school().count()

    @admin.display(description=_('Primary'))
    def children_in_primary_count(self, active_course):
        return Child.objects.in_primary().count()

    @admin.display(description=_('HH members'))
    def hh_members(self, active_course):
        min_age = Level.AGE_HH2
        max_age = Level.AGE_HH5
        child_count = Child.objects.by_age_range(min_age, max_age).count()
        members_count = Membership.objects.by_child_age_range(min_age, max_age).count()
        return f'{members_count}/{child_count}'

    @admin.display(description=_('HH2 members'))
    def hh2_members(self, active_course):
        age = Level.AGE_HH2
        child_count = Child.objects.by_age(age).count()
        members_count = Membership.objects.by_child_age(age).count()
        return f'{members_count}/{child_count}'
    
    @admin.display(description=_('HH3 members'))
    def hh3_members(self, active_course):
        age = Level.AGE_HH3
        child_count = Child.objects.by_age(age).count()
        members_count = Membership.objects.by_child_age(age).count()
        return f'{members_count}/{child_count}'

    @admin.display(description=_('HH4 members'))
    def hh4_members(self, active_course):
        age = Level.AGE_HH4
        child_count = Child.objects.by_age(age).count()
        members_count = Membership.objects.by_child_age(age).count()
        return f'{members_count}/{child_count}'

    @admin.display(description=_('HH5 members'))
    def hh5_members(self, active_course):
        age = Level.AGE_HH5
        child_count = Child.objects.by_age(age).count()
        members_count = Membership.objects.by_child_age(age).count()
        return f'{members_count}/{child_count}'
    
    @admin.display(description=_('LH members'))
    def lh_members(self, active_course):
        min_age = Level.AGE_LH1
        max_age = Level.AGE_LH6
        child_count = Child.objects.by_age_range(min_age, max_age).count()
        members_count = Membership.objects.by_child_age_range(min_age, max_age).count()
        return f'{members_count}/{child_count}'

    @admin.display(description=_('LH1 members'))
    def lh1_members(self, active_course):
        age = Level.AGE_LH1
        child_count = Child.objects.by_age(age).count()
        members_count = Membership.objects.by_child_age(age).count()
        return f'{members_count}/{child_count}'
    
    @admin.display(description=_('LH2 members'))
    def lh2_members(self, active_course):
        age = Level.AGE_LH2
        child_count = Child.objects.by_age(age).count()
        members_count = Membership.objects.by_child_age(age).count()
        return f'{members_count}/{child_count}'

    @admin.display(description=_('LH3 members'))
    def lh3_members(self, active_course):
        age = Level.AGE_LH3
        child_count = Child.objects.by_age(age).count()
        members_count = Membership.objects.by_child_age(age).count()
        return f'{members_count}/{child_count}'

    @admin.display(description=_('LH4 members'))
    def lh4_members(self, active_course):
        age = Level.AGE_LH4
        child_count = Child.objects.by_age(age).count()
        members_count = Membership.objects.by_child_age(age).count()
        return f'{members_count}/{child_count}'

    @admin.display(description=_('LH5 members'))
    def lh5_members(self, active_course):
        age = Level.AGE_LH5
        child_count = Child.objects.by_age(age).count()
        members_count = Membership.objects.by_child_age(age).count()
        return f'{members_count}/{child_count}'

    @admin.display(description=_('LH6 members'))
    def lh6_members(self, active_course):
        age = Level.AGE_LH6
        child_count = Child.objects.by_age(age).count()
        members_count = Membership.objects.by_child_age(age).count()
        return f'{members_count}/{child_count}'
