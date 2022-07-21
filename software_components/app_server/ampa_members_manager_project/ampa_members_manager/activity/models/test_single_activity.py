from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.activity.models.repetitive_activity import RepetitiveActivity
from ampa_members_manager.activity.models.single_activity import SingleActivity, PaymentType
from ampa_members_manager.baker_recipes import single_activity_with_repetitive_activity, \
    single_activity_with_unique_activity


class TestSingleActivity(TestCase):
    def test_str(self):
        single_activity: SingleActivity = baker.make_recipe(single_activity_with_unique_activity)

        self.assertEqual(str(single_activity), single_activity.name)

    def test_calculate_price_single_member(self):
        single_activity: SingleActivity = baker.make_recipe(
            single_activity_with_unique_activity, payment_type=PaymentType.SINGLE)
        times: float = 2.5

        price: float = single_activity.calculate_price(times, True)

        self.assertEqual(price, float(single_activity.price_for_member))

    def test_calculate_price_single_no_member(self):
        single_activity: SingleActivity = baker.make_recipe(
            single_activity_with_unique_activity, payment_type=PaymentType.SINGLE)
        times: float = 2.5

        price: float = single_activity.calculate_price(times, False)

        self.assertEqual(price, float(single_activity.price_for_no_member))

    def test_calculate_price_per_day_member(self):
        single_activity: SingleActivity = baker.make_recipe(
            single_activity_with_unique_activity, payment_type=PaymentType.PER_DAY)
        times: float = 2.5

        price: float = single_activity.calculate_price(times, True)

        self.assertEqual(price, float(single_activity.price_for_member) * times)

    def test_calculate_price_per_day_no_member(self):
        single_activity: SingleActivity = baker.make_recipe(
            single_activity_with_unique_activity, payment_type=PaymentType.PER_DAY)
        times: float = 2.5

        price: float = single_activity.calculate_price(times, False)

        self.assertEqual(price, float(single_activity.price_for_no_member) * times)

    def test_all_same_repetitive_activity_no_single_activity(self):
        same: bool = SingleActivity.all_same_repetitive_activity(SingleActivity.objects.all())

        self.assertTrue(same)

    def test_all_same_repetitive_activity_one_single_activity_unique(self):
        baker.make_recipe(single_activity_with_unique_activity)

        same: bool = SingleActivity.all_same_repetitive_activity(SingleActivity.objects.all())

        self.assertTrue(same)

    def test_all_same_repetitive_activity_one_single_activity_repetitive(self):
        baker.make_recipe(single_activity_with_repetitive_activity)

        same: bool = SingleActivity.all_same_repetitive_activity(SingleActivity.objects.all())

        self.assertTrue(same)

    def test_all_same_repetitive_activity_two_single_activity_with_one_unique_activity(self):
        baker.make_recipe(single_activity_with_unique_activity)
        baker.make_recipe(single_activity_with_repetitive_activity)

        same: bool = SingleActivity.all_same_repetitive_activity(SingleActivity.objects.all())

        self.assertFalse(same)

    def test_all_same_repetitive_activity_two_single_activity_with_same_repetitive_activity(self):
        repetitive_activity: RepetitiveActivity = baker.make('RepetitiveActivity')
        baker.make('SingleActivity', repetitive_activity=repetitive_activity)
        baker.make('SingleActivity', repetitive_activity=repetitive_activity)

        same: bool = SingleActivity.all_same_repetitive_activity(SingleActivity.objects.all())

        self.assertTrue(same)

    def test_all_same_repetitive_activity_two_single_activity_with_different_repetitive_activity(self):
        baker.make_recipe(single_activity_with_repetitive_activity)
        baker.make_recipe(single_activity_with_repetitive_activity)

        same: bool = SingleActivity.all_same_repetitive_activity(SingleActivity.objects.all())

        self.assertFalse(same)
