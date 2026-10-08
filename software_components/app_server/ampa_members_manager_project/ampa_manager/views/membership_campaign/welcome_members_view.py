from django.conf import settings
from django.shortcuts import render
from django.urls import reverse

from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.charge.use_cases.membership.mail_notifier_result import MailNotifierResult
from ampa_manager.charge.use_cases.membership.membership_welcome_notifier import MembershipWelcomeNotifier
from ampa_manager.family.models.membership import Membership
from ampa_manager.views.membership_campaign.base_membership_campaign_view import BaseMembershipCampaignView


class WelcomeMembersView(BaseMembershipCampaignView):
    HTML_TEMPLATE = 'membership_campaign/welcome_members.html'
    VIEW_NAME = 'welcome_members'

    @classmethod
    def get_context(cls) -> dict:
        context = super().get_context()
        context.update({
            'members_count': cls.get_active_course_members_count(),
            'members_url': cls.get_active_course_members_url(),
            'test_email': settings.TEST_EMAIL_RECIPIENT,
        })
        return context

    @classmethod
    def get(cls, request):
        return render(request, cls.HTML_TEMPLATE, cls.get_context())

    @classmethod
    def post(cls, request):
        result: MailNotifierResult = MembershipWelcomeNotifier(is_a_test=cls.is_a_test(request)).notify()

        context = cls.get_context()
        context['result'] = result
        return render(request, cls.HTML_TEMPLATE, context)

    @classmethod
    def get_active_course_members_url(cls):
        year = ActiveCourse.get_active_course_initial_year()
        return reverse('admin:ampa_manager_membership_changelist') + f'?academic_course__initial_year={year}'

    @classmethod
    def get_active_course_members_count(cls) -> int:
        return Membership.objects.of_active_course().count()

    @classmethod
    def is_a_test(cls, request):
        return request.GET.get('test') == 'true'
