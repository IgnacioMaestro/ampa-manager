from django.conf import settings
from django.shortcuts import render
from django.urls import reverse

from ampa_manager.charge.use_cases.membership.mail_notifier_result import MailNotifierResult
from ampa_manager.charge.use_cases.membership.membership_campaign_notifier import MembershipCampaignNotifier
from ampa_manager.family.models.family import Family
from ampa_manager.views.membership_campaign.base_membership_campaign_view import BaseMembershipCampaignView


class OpenMembershipCampaignView(BaseMembershipCampaignView):
    HTML_TEMPLATE = 'membership_campaign/open_membership_campaign.html'
    VIEW_NAME = 'open_members_campaign'

    @classmethod
    def get_context(cls) -> dict:
        context = super().get_context()
        context.update({})
        return context

    @classmethod
    def get(cls, request):
        return render(request, cls.HTML_TEMPLATE, cls.get_context())
