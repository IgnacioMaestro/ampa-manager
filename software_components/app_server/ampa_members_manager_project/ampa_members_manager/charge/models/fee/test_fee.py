from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.charge.models.fee.fee import Fee


class TestFee(TestCase):
    def test_str(self):
        fee: Fee = baker.make('Fee')

        self.assertEqual(str(fee), str(fee.academic_course))
