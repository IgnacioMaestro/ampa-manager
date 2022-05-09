from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.activity.models.single_activity import SingleActivity, PaymentType


class TestSingleActivity(TestCase):
    def test_str(self):
        single_activity: SingleActivity = baker.make('SingleActivity')
        self.assertEqual(str(single_activity), single_activity.name)

    def test_calculate_price_single_member(self):
        single_activity: SingleActivity = baker.make('SingleActivity', payment_type=PaymentType.SINGLE)
        times: float = 2.5
        price: float = single_activity.calculate_price(times, True)
        self.assertEqual(price, float(single_activity.price_for_member))

    def test_calculate_price_single_no_member(self):
        single_activity: SingleActivity = baker.make('SingleActivity', payment_type=PaymentType.SINGLE)
        times: float = 2.5
        price: float = single_activity.calculate_price(times, False)
        self.assertEqual(price, float(single_activity.price_for_no_member))

    def test_calculate_price_per_day_member(self):
        single_activity: SingleActivity = baker.make('SingleActivity', payment_type=PaymentType.PER_DAY)
        times: float = 2.5
        price: float = single_activity.calculate_price(times, True)
        self.assertEqual(price, float(single_activity.price_for_member) * times)

    def test_calculate_price_per_day_no_member(self):
        single_activity: SingleActivity = baker.make('SingleActivity', payment_type=PaymentType.PER_DAY)
        times: float = 2.5
        price: float = single_activity.calculate_price(times, False)
        self.assertEqual(price, float(single_activity.price_for_no_member)   * times)
