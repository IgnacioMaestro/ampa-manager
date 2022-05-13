from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.academic_course.models.fee import Fee


class TestFee(TestCase):
    def test_str(self):
        fee: Fee = baker.make('Fee')
        self.assertEqual(str(fee), f'{str(fee.year)}')
