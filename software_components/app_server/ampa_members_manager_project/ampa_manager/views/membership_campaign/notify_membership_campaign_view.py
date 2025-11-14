from django.conf import settings
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from ampa_manager.charge.use_cases.membership.membership_campaign_notifier import MembershipCampaignNotifier
from ampa_manager.family.models.family import Family


class NotifyMembershipCampaignView(View):
    HTML_TEMPLATE = 'membership_campaign/notify_membership_campaign.html'
    VIEW_NAME = 'notify_members_campaign'

    @classmethod
    def get_context(cls) -> dict:
        family_changelist_url = reverse('admin:ampa_manager_family_changelist')
        return {
            'current_step': cls.VIEW_NAME,
            'families_renew_count': Family.objects.membership_renew().count(),
            'families_not_renew_out_of_school_count': Family.objects.membership_no_renew_no_school_children().count(),
            'families_not_renew_declined_count': Family.objects.membership_no_renew_declined().count(),
            'families_renew_url': f'{family_changelist_url}?member=renew',
            'families_not_renew_out_of_school_url': f'{family_changelist_url}?member=no_renew_no_school_children',
            'families_not_renew_declined_url': f'{family_changelist_url}?member=no_renew_declined',
            'test_email': settings.TEST_EMAIL_RECIPIENT,
        }

    @classmethod
    def get(cls, request):
        return render(request, cls.HTML_TEMPLATE, cls.get_context())

    @classmethod
    def post(cls, request):
        is_a_test = request.GET.get("test") == "true"
        context = cls.get_context()
        if is_a_test:
            context['result'] = MembershipCampaignNotifier().test_notify()
        else:
            context['result'] = MembershipCampaignNotifier().notify()
        return render(request, cls.HTML_TEMPLATE, context)
