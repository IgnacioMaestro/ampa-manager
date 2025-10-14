from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy
from django.views import View

from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.charge.use_cases.membership.membership_campaign_copier import MembershipCampaignCopier
from ampa_manager.family.models.family import Family


class ImportLastCourseMembersView(View):
    HTML_TEMPLATE = 'copy_last_course_members.html'
    VIEW_NAME = 'copy_last_course_members'

    @classmethod
    def get_context(cls) -> dict:
        family_changelist_url = reverse('admin:ampa_manager_family_changelist')
        return {
            'families_renew_count': Family.objects.membership_renew().count(),
            'families_not_renew_out_of_school_count': Family.objects.membership_no_renew_no_school_children().count(),
            'families_not_renew_declined_count': Family.objects.membership_no_renew_declined().count(),
            'families_renew_url': f'{family_changelist_url}?member=renew',
            'families_not_renew_out_of_school_url': f'{family_changelist_url}?member=no_renew_no_school_children',
            'families_not_renew_declined_url': f'{family_changelist_url}?member=no_renew_declined',
        }

    @classmethod
    def get(cls, request):
        return render(request, cls.HTML_TEMPLATE, cls.get_context())

    @classmethod
    def post(cls, request):
        if MembershipCampaignCopier().copy_members_from_last_course():
            messages.info(request, gettext_lazy('Active course members updated'))
        else:
            messages.error(request, gettext_lazy('Unable to update active course members'))

        return redirect(cls.get_active_course_members_url())

    @classmethod
    def get_active_course_members_url(cls) -> str:
        year = ActiveCourse.get_active_course_initial_year()
        return reverse('admin:ampa_manager_membership_changelist') + f'?academic_course__initial_year={year}'
