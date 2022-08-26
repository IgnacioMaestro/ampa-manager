from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.activity.models.activity import Activity
from ampa_members_manager.activity.models.activity_period import ActivityPeriod
from ampa_members_manager.activity.models.payment_type import PaymentType


class TestActivityPeriod(TestCase):
    def test_str(self):
        activity_period: ActivityPeriod = baker.prepare('ActivityPeriod')

        self.assertEqual(str(activity_period), activity_period.name)

    def test_calculate_price_single_member(self):
        activity_period: ActivityPeriod = baker.prepare('ActivityPeriod', payment_type=PaymentType.SINGLE)
        times: float = 2.5

        price: float = activity_period.calculate_price(times, True)

        self.assertEqual(price, float(activity_period.price_for_member))

    def test_calculate_price_single_no_member(self):
        activity_period: ActivityPeriod = baker.prepare('ActivityPeriod', payment_type=PaymentType.SINGLE)
        times: float = 2.5

        price: float = activity_period.calculate_price(times, False)

        self.assertEqual(price, float(activity_period.price_for_no_member))

    def test_calculate_price_per_day_member(self):
        activity_period: ActivityPeriod = baker.prepare('ActivityPeriod', payment_type=PaymentType.PER_DAY)
        times: float = 2.5

        price: float = activity_period.calculate_price(times, True)

        self.assertEqual(price, float(activity_period.price_for_member) * times)

    def test_calculate_price_per_day_no_member(self):
        activity_period: ActivityPeriod = baker.prepare('ActivityPeriod', payment_type=PaymentType.PER_DAY)
        times: float = 2.5

        price: float = activity_period.calculate_price(times, False)

        self.assertEqual(price, float(activity_period.price_for_no_member) * times)

    def test_all_same_activity_no_activity_period(self):
        same: bool = ActivityPeriod.all_same_activity(ActivityPeriod.objects.all())

        self.assertTrue(same)

    def test_all_same_activity_one_activity_period(self):
        baker.make('ActivityPeriod')

        same: bool = ActivityPeriod.all_same_activity(ActivityPeriod.objects.all())

        self.assertTrue(same)

    def test_all_same_activity_two_activity_periods_with_different_activity(self):
        baker.make('ActivityPeriod')
        baker.make('ActivityPeriod')

        same: bool = ActivityPeriod.all_same_activity(ActivityPeriod.objects.all())

        self.assertFalse(same)

    def test_all_same_activity_two_activity_periods_with_same_activity(self):
        activity: Activity = baker.make('Activity')
        baker.make('ActivityPeriod', activity=activity)
        baker.make('ActivityPeriod', activity=activity)

        same: bool = ActivityPeriod.all_same_activity(ActivityPeriod.objects.all())

        self.assertTrue(same)
