from typing import Optional

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy
from django.views import View

from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.charge.models.fee.fee import Fee
from ampa_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_manager.charge.use_cases.membership.membership_remittance_notifier import MembershipRemittanceNotifier
from ampa_manager.family.models.membership import Membership


class NotifyMembersRemittanceView(View):
    HTML_TEMPLATE = 'membership_campaign/notify_membership_remittance.html'
    VIEW_NAME = 'notify_members_remittance'

    @classmethod
    def get_context(cls, remittance_id: Optional[int]) -> dict:
        return {
            'current_step': cls.VIEW_NAME,
            'active_course_fee': cls.get_active_course_fee(),
            'active_course_members': cls.get_active_course_members_count(),
            'active_course_members_url': cls.get_active_course_members_url(),
            'fee_url': reverse('admin:ampa_manager_fee_changelist'),
            'test_email': settings.TEST_EMAIL_RECIPIENT,
            'remittance_id': remittance_id,
        }

    @classmethod
    def get(cls, request):
        return render(request, cls.HTML_TEMPLATE, cls.get_context())

    @classmethod
    def post(cls, request):
        try:
            remittance_id = request.GET.get('remittance_id')
            remittance = MembershipRemittance.objects.get(id=remittance_id)

            error: Optional[str] = MembershipRemittanceNotifier(remittance).notify()
            if not error:
                messages.info(request, gettext_lazy('Remittance notified'))
            else:
                messages.error(request, gettext_lazy('Unable to notify remittance') + f': {error}')
        except MembershipRemittance.DoesNotExist:
            messages.error(request, gettext_lazy('Remittance not found'))

        return redirect(reverse('admin:ampa_manager_membershipremittance_changelist'))

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
