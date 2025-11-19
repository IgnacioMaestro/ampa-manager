from typing import Optional

from django.conf import settings
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.charge.models.fee.fee import Fee
from ampa_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_manager.charge.use_cases.membership.mail_notifier_result import MailNotifierResult
from ampa_manager.charge.use_cases.membership.membership_remittance_notifier import MembershipRemittanceNotifier
from ampa_manager.family.models.membership import Membership
from ampa_manager.views.membership_campaign.base_membership_campaign_view import BaseMembershipCampaignView


class NotifyMembersRemittanceView(BaseMembershipCampaignView):
    HTML_TEMPLATE = 'membership_campaign/notify_membership_remittance.html'
    VIEW_NAME = 'notify_members_remittance'

    @classmethod
    def get_extra_context(cls) -> dict:
        remittance: MembershipRemittance = cls.get_active_course_remittance()
        if remittance:
            remittance_url = reverse('admin:ampa_manager_membershipremittance_change', args=[remittance.id])
            remittance_str = str(remittance)
        else:
            remittance_url = None
            remittance_str = _('Not yet generated')

        return {
            'active_course_fee': cls.get_active_course_fee(),
            'active_course_members': cls.get_active_course_members_count(),
            'active_course_members_url': cls.get_active_course_members_url(),
            'active_course_remittance_name': remittance_str,
            'active_course_remittance_url': remittance_url,
            'active_course_remittances_url': cls.get_active_course_remittances_url(),
            'active_course_remittances_count': cls.get_active_course_remittances_count(),
            'fee_url': reverse('admin:ampa_manager_fee_changelist'),
            'test_email': settings.TEST_EMAIL_RECIPIENT,
        }

    @classmethod
    def get(cls, request):
        return render(request, cls.HTML_TEMPLATE, cls.get_context())

    @classmethod
    def post(cls, request):
        remittance: MembershipRemittance = cls.get_active_course_remittance()
        if remittance:
            if cls.is_a_test(request):
                result: MailNotifierResult = MembershipRemittanceNotifier(remittance).test_notify()
            else:
                result: MailNotifierResult = MembershipRemittanceNotifier(remittance).notify()
        else:
            result = None

        context = cls.get_context()
        context['result'] = result
        return render(request, cls.HTML_TEMPLATE, context)

    @classmethod
    def get_active_course_members_url(cls):
        year = ActiveCourse.get_active_course_initial_year()
        return reverse('admin:ampa_manager_membership_changelist') + f'?academic_course__initial_year={year}'

    @classmethod
    def get_active_course_members_count(cls) -> int:
        active_course = ActiveCourse.load()
        return Membership.objects.of_course(active_course).count()

    @classmethod
    def get_active_course_fee(cls) -> int:
        active_course = ActiveCourse.load()
        try:
            return Fee.objects.get(academic_course=active_course).amount
        except Fee.DoesNotExist:
            return 0

    @classmethod
    def get_active_course_remittance(cls) -> Optional[MembershipRemittance]:
        active_course = ActiveCourse.load()
        return MembershipRemittance.objects.of_course(active_course).order_by('-id').first()

    @classmethod
    def get_active_course_remittances_count(cls) -> int:
        active_course = ActiveCourse.load()
        return MembershipRemittance.objects.of_course(active_course).count()

    @classmethod
    def get_active_course_remittances_url(cls):
        return reverse('admin:ampa_manager_membershipremittance_changelist')

    @classmethod
    def is_a_test(cls, request):
        return request.GET.get("test") == "true"
