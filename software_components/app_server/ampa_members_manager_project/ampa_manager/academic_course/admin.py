from typing import Optional

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, gettext_lazy

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.academic_course.models.level import Level
from ampa_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_manager.charge.use_cases.membership.create_membership_remittance_with_families.membership_remittance_creator import \
    MembershipRemittanceCreator, MembershipRemittanceCreatorError
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.membership import Membership
from ampa_manager.family.models.parent import Parent
from ampa_manager.statistics.models import Statistic
from ampa_manager.utils.utils import Utils


class AcademicCourseAdmin(admin.ModelAdmin):
    list_display = ['summary', 'is_active', 'members_count']
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

    @admin.action(description=gettext_lazy("Generate remesa de socios"))
    def generate_remittance(self, request, academic_courses: QuerySet[AcademicCourse]):
        if academic_courses.count() > 1:
            message = gettext_lazy("Select the courses one by one")
            return self.message_user(request=request, message=message)

        academic_course: AcademicCourse = academic_courses.first()
        families_to_renew = Family.objects.renew_membership()
        remittance: Optional[MembershipRemittance]
        remittance_error: Optional[MembershipRemittanceCreatorError]
        remittance, remittance_error = MembershipRemittanceCreator(families_to_renew, academic_course).create()
        if not remittance:
            if remittance_error == MembershipRemittanceCreatorError.NO_FAMILIES:
                message = gettext_lazy("No families to include in Membership Remittance")
            else:
                if remittance_error == MembershipRemittanceCreatorError.BIC_ERROR:
                    link = Utils.get_model_link(
                        model_name=BankAccount.__name__.lower(),
                        link_text=gettext_lazy("Review the Bank Accounts without BIC"), filters='bic=without')
                    message = mark_safe(gettext_lazy("BIC error") + " " + link)
                else:
                    message = gettext_lazy("Membership Remittance error")
            return self.message_user(request=request, message=message, level=messages.ERROR)
        else:
            message = mark_safe(
                gettext_lazy(
                    "Membership remittance created") + " (<a href=\"" + remittance.get_admin_url() + "\">" + gettext_lazy(
                    "View details") + "</a>)")
            return self.message_user(request=request, message=message)

    actions = [generate_remittance]

class ActiveCourseAdmin(admin.ModelAdmin):
    list_display = ['course', 'members_count', 'families_in_school_count', 'parents_count', 'children_in_school_count']
    readonly_fields = ['members_count', 'families_in_school_count', 'parents_count', 'children_in_school_count',
                       'children_in_pre_school_count', 'children_in_primary_count', 'children_out_of_school_count',
                       'hh_members', 'hh2_members', 'hh3_members', 'hh4_members', 'hh5_members', 'lh_members',
                       'lh1_members', 'lh2_members', 'lh3_members', 'lh4_members', 'lh5_members', 'lh6_members']
    fieldsets = (
        (None, {
            'fields': ('course',)
        }),
        (_('Families'), {
            'fields': ('members_count', 'families_in_school_count', 'parents_count'),
        }),
        (_('Students'), {
            'fields': ('children_in_school_count', 'children_in_pre_school_count', 'children_in_primary_count',
                       'children_out_of_school_count'),
        }),
        (_('HH members'), {
            'fields': ('hh_members', 'hh2_members', 'hh3_members', 'hh4_members', 'hh5_members'),
        }),
        (_('LH members'), {
            'fields': (
                'lh_members', 'lh1_members', 'lh2_members', 'lh3_members', 'lh4_members', 'lh5_members', 'lh6_members'),
        }),
    )

    @admin.display(description=_('Members'))
    def members_count(self, _):
        return Membership.objects.of_active_course().count()

    @admin.display(description=_('Families'))
    def families_count(self, _):
        return Family.objects.count()

    @admin.display(description=_('Families with children in school'))
    def families_in_school_count(self, _):
        return Statistic.families_in_school()

    @admin.display(description=_('Parents'))
    def parents_count(self, _):
        return Parent.objects.count()

    @admin.display(description=_('Children in school'))
    def children_in_school_count(self, _):
        return Statistic.children_in_school()

    @admin.display(description=_('Pre-school'))
    def children_in_pre_school_count(self, _):
        return Child.objects.in_pre_school().count()

    @admin.display(description=_('Primary'))
    def children_in_primary_count(self, _):
        return Child.objects.in_primary().count()

    @admin.display(description=_('Out of school'))
    def children_out_of_school_count(self, _):
        return Child.objects.out_of_school().count()

    @admin.display(description=_('HH members'))
    def hh_members(self, _):
        return Statistic.get_hh_members_by_total()

    @admin.display(description=_('HH2 members'))
    def hh2_members(self, _):
        return Statistic.get_level_members_by_total(Level.ID_HH2)

    @admin.display(description=_('HH3 members'))
    def hh3_members(self, _):
        return Statistic.get_level_members_by_total(Level.ID_HH3)

    @admin.display(description=_('HH4 members'))
    def hh4_members(self, _):
        return Statistic.get_level_members_by_total(Level.ID_HH4)

    @admin.display(description=_('HH5 members'))
    def hh5_members(self, _):
        return Statistic.get_level_members_by_total(Level.ID_HH5)

    @admin.display(description=_('LH members'))
    def lh_members(self, _):
        return Statistic.get_lh_members_by_total()

    @admin.display(description=_('LH1 members'))
    def lh1_members(self, _):
        return Statistic.get_level_members_by_total(Level.ID_LH1)

    @admin.display(description=_('LH2 members'))
    def lh2_members(self, _):
        return Statistic.get_level_members_by_total(Level.ID_LH2)

    @admin.display(description=_('LH3 members'))
    def lh3_members(self, _):
        return Statistic.get_level_members_by_total(Level.ID_LH3)

    @admin.display(description=_('LH4 members'))
    def lh4_members(self, _):
        return Statistic.get_level_members_by_total(Level.ID_LH4)

    @admin.display(description=_('LH5 members'))
    def lh5_members(self, _):
        return Statistic.get_level_members_by_total(Level.ID_LH5)

    @admin.display(description=_('LH6 members'))
    def lh6_members(self, _):
        return Statistic.get_level_members_by_total(Level.ID_LH6)
