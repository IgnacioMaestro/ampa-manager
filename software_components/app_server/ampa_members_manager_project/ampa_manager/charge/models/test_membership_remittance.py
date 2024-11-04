from django.test import TestCase
from django.utils.timezone import now
from model_bakery import baker

from ampa_manager.charge.models.membership_remittance import MembershipRemittance


class TestMembershipRemittance(TestCase):
    def test_complete_name(self):
        datetime = now()
        membership_remittance: MembershipRemittance = baker.prepare(MembershipRemittance, created_at=datetime)
        self.assertEqual(
            membership_remittance.complete_name,
            str(membership_remittance.course) + ' - ' + datetime.strftime("%Y%m%d_%H%M%S"))
