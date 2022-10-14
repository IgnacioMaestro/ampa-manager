import imp
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.family.models.membership import Membership
from ampa_members_manager.family.models.parent import Parent
from ampa_members_manager.family.models.child import Child
from ampa_members_manager.academic_course.models.course_name import CourseName
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
    list_display = ['course', 'members_count', 'families_count', 'parents_count', 'children_count', 'hh_members', 'hh2_members', 'hh3_members', 'hh4_members', 'hh5_members', 'lh_members', 'lh1_members', 'lh2_members', 'lh3_members', 'lh4_members', 'lh5_members', 'lh6_members']
    readonly_fields = ['members_count', 'families_count', 'parents_count', 'children_count', 'hh_members', 'hh2_members', 'hh3_members', 'hh4_members', 'hh5_members', 'lh_members', 'lh1_members', 'lh2_members', 'lh3_members', 'lh4_members', 'lh5_members', 'lh6_members']
    fieldsets = (
        (None, {
            'fields': ('course',)
        }),
        (_('Global'), {
            'fields': ('members_count', 'families_count', 'parents_count', 'children_count'),
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
        return Membership.objects.filter(academic_course=active_course.course).count()
    
    @admin.display(description=_('Families'))
    def families_count(self, active_course):
        return Family.objects.count()
    
    @admin.display(description=_('Parents'))
    def parents_count(self, active_course):
        return Parent.objects.count()
    
    @admin.display(description=_('Children'))
    def children_count(self, active_course):
        return Child.objects.count()

    @admin.display(description=_('HH members'))
    def hh_members(self, active_course):
        min_age = CourseName.AGE_HH2
        max_age = CourseName.AGE_HH5
        child_count = Child.objects.by_age_range(min_age, max_age).count()
        members_count = Membership.objects.by_child_age_range(min_age, max_age).count()
        return f'{members_count}/{child_count}'

    @admin.display(description=_('HH2 members'))
    def hh2_members(self, active_course):
        age = CourseName.AGE_HH2
        child_count = Child.objects.by_age(age).count()
        members_count = Membership.objects.by_child_age(age).count()
        return f'{members_count}/{child_count}'
    
    @admin.display(description=_('HH3 members'))
    def hh3_members(self, active_course):
        age = CourseName.AGE_HH3
        child_count = Child.objects.by_age(age).count()
        members_count = Membership.objects.by_child_age(age).count()
        return f'{members_count}/{child_count}'

    @admin.display(description=_('HH4 members'))
    def hh4_members(self, active_course):
        age = CourseName.AGE_HH4
        child_count = Child.objects.by_age(age).count()
        members_count = Membership.objects.by_child_age(age).count()
        return f'{members_count}/{child_count}'

    @admin.display(description=_('HH5 members'))
    def hh5_members(self, active_course):
        age = CourseName.AGE_HH5
        child_count = Child.objects.by_age(age).count()
        members_count = Membership.objects.by_child_age(age).count()
        return f'{members_count}/{child_count}'
    
    @admin.display(description=_('LH members'))
    def lh_members(self, active_course):
        min_age = CourseName.AGE_LH1
        max_age = CourseName.AGE_LH6
        child_count = Child.objects.by_age_range(min_age, max_age).count()
        members_count = Membership.objects.by_child_age_range(min_age, max_age).count()
        return f'{members_count}/{child_count}'

    @admin.display(description=_('LH1 members'))
    def lh1_members(self, active_course):
        age = CourseName.AGE_LH1
        child_count = Child.objects.by_age(age).count()
        members_count = Membership.objects.by_child_age(age).count()
        return f'{members_count}/{child_count}'
    
    @admin.display(description=_('LH2 members'))
    def lh2_members(self, active_course):
        age = CourseName.AGE_LH2
        child_count = Child.objects.by_age(age).count()
        members_count = Membership.objects.by_child_age(age).count()
        return f'{members_count}/{child_count}'

    @admin.display(description=_('LH3 members'))
    def lh3_members(self, active_course):
        age = CourseName.AGE_LH3
        child_count = Child.objects.by_age(age).count()
        members_count = Membership.objects.by_child_age(age).count()
        return f'{members_count}/{child_count}'

    @admin.display(description=_('LH4 members'))
    def lh4_members(self, active_course):
        age = CourseName.AGE_LH4
        child_count = Child.objects.by_age(age).count()
        members_count = Membership.objects.by_child_age(age).count()
        return f'{members_count}/{child_count}'

    @admin.display(description=_('LH5 members'))
    def lh5_members(self, active_course):
        age = CourseName.AGE_LH5
        child_count = Child.objects.by_age(age).count()
        members_count = Membership.objects.by_child_age(age).count()
        return f'{members_count}/{child_count}'

    @admin.display(description=_('LH6 members'))
    def lh6_members(self, active_course):
        age = CourseName.AGE_LH6
        child_count = Child.objects.by_age(age).count()
        members_count = Membership.objects.by_child_age(age).count()
        return f'{members_count}/{child_count}'
