from typing import Optional

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy
from rest_framework.views import APIView
from rest_framework import permissions, status
from ampa_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_manager.charge.use_cases.membership.membership_remittance_notifier import MembershipRemittanceNotifier


class NotifyMembersRemittanceView(APIView):
    permission_classes = [permissions.IsAdminUser]

    @classmethod
    def get(cls, request):
        try:
            remittance = MembershipRemittance.objects.get(id=request.GET['remittance_id'])

            error: Optional[str] = MembershipRemittanceNotifier(remittance).notify()
            if not error:
                messages.info(request, gettext_lazy('Remittance notified'))
            else:
                messages.error(request, gettext_lazy('Unable to notify remittance') + f': {error}')
        except MembershipRemittance.DoesNotExist:
            messages.error(request, gettext_lazy('Remittance not found'))

        return redirect(reverse('admin:ampa_manager_membershipremittance_changelist'))
