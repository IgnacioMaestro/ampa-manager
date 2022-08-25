from django.db import IntegrityError
from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.activity.models.repetitive_activity import RepetitiveActivity
from ampa_members_manager.activity.models.activity_period import ActivityPeriod, PaymentType
from ampa_members_manager.baker_recipes import payable_part_with_repetitive_activity, \
    payable_part_with_unique_activity


class TestActivityPeriod(TestCase):
    def test_one_activity_reference_constraint_no_repetitive_neither_unique(self):
        with self.assertRaises(IntegrityError):
            baker.make('ActivityPeriod')

    def test_one_activity_reference_constraint_with_repetitive_and_unique(self):
        with self.assertRaises(IntegrityError):
            repetitive_activity = baker.make('RepetitiveActivity')
            unique_activity = baker.make('UniqueActivity')
            ActivityPeriod.objects.create(
                name='name', price_for_member=50, price_for_no_member=150, payment_type=PaymentType.SINGLE,
                repetitive_activity=repetitive_activity, unique_activity=unique_activity)

    def test_str(self):
        payable_part: ActivityPeriod = baker.prepare_recipe(payable_part_with_unique_activity)

        self.assertEqual(str(payable_part), payable_part.name)

    def test_calculate_price_single_member(self):
        payable_part: ActivityPeriod = baker.prepare_recipe(
            payable_part_with_unique_activity, payment_type=PaymentType.SINGLE)
        times: float = 2.5

        price: float = payable_part.calculate_price(times, True)

        self.assertEqual(price, float(payable_part.price_for_member))

    def test_calculate_price_single_no_member(self):
        payable_part: ActivityPeriod = baker.prepare_recipe(
            payable_part_with_unique_activity, payment_type=PaymentType.SINGLE)
        times: float = 2.5

        price: float = payable_part.calculate_price(times, False)

        self.assertEqual(price, float(payable_part.price_for_no_member))

    def test_calculate_price_per_day_member(self):
        payable_part: ActivityPeriod = baker.prepare_recipe(
            payable_part_with_unique_activity, payment_type=PaymentType.PER_DAY)
        times: float = 2.5

        price: float = payable_part.calculate_price(times, True)

        self.assertEqual(price, float(payable_part.price_for_member) * times)

    def test_calculate_price_per_day_no_member(self):
        payable_part: ActivityPeriod = baker.prepare_recipe(
            payable_part_with_unique_activity, payment_type=PaymentType.PER_DAY)
        times: float = 2.5

        price: float = payable_part.calculate_price(times, False)

        self.assertEqual(price, float(payable_part.price_for_no_member) * times)

    def test_all_same_repetitive_activity_no_payable_part(self):
        same: bool = ActivityPeriod.all_same_repetitive_activity(ActivityPeriod.objects.all())

        self.assertTrue(same)

    def test_all_same_repetitive_activity_one_payable_part_unique(self):
        baker.make_recipe(payable_part_with_unique_activity)

        same: bool = ActivityPeriod.all_same_repetitive_activity(ActivityPeriod.objects.all())

        self.assertTrue(same)

    def test_all_same_repetitive_activity_one_payable_part_repetitive(self):
        baker.make_recipe(payable_part_with_repetitive_activity)

        same: bool = ActivityPeriod.all_same_repetitive_activity(ActivityPeriod.objects.all())

        self.assertTrue(same)

    def test_all_same_repetitive_activity_two_payable_part_with_one_unique_activity(self):
        baker.make_recipe(payable_part_with_unique_activity)
        baker.make_recipe(payable_part_with_repetitive_activity)

        same: bool = ActivityPeriod.all_same_repetitive_activity(ActivityPeriod.objects.all())

        self.assertFalse(same)

    def test_all_same_repetitive_activity_two_payable_part_with_same_repetitive_activity(self):
        repetitive_activity: RepetitiveActivity = baker.make('RepetitiveActivity')
        baker.make('ActivityPeriod', repetitive_activity=repetitive_activity)
        baker.make('ActivityPeriod', repetitive_activity=repetitive_activity)

        same: bool = ActivityPeriod.all_same_repetitive_activity(ActivityPeriod.objects.all())

        self.assertTrue(same)

    def test_all_same_repetitive_activity_two_payable_part_with_different_repetitive_activity(self):
        baker.make_recipe(payable_part_with_repetitive_activity)
        baker.make_recipe(payable_part_with_repetitive_activity)

        same: bool = ActivityPeriod.all_same_repetitive_activity(ActivityPeriod.objects.all())

        self.assertFalse(same)
