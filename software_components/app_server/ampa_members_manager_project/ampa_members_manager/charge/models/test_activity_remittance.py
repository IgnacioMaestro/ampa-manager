from django.db.models import QuerySet
from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.activity.models.activity_payable_part import ActivityPayablePart
from ampa_members_manager.baker_recipes import payable_part_with_unique_activity
from ampa_members_manager.charge.models.activity_remittance import ActivityRemittance
from ampa_members_manager.charge.no_payable_part_error import NoActivityPayablePartError


class TestActivityRemittance(TestCase):
    def test_create_filled_no_payable_part(self):
        payable_parts_none: QuerySet[ActivityPayablePart] = ActivityPayablePart.objects.none()
        with self.assertRaises(NoActivityPayablePartError):
            ActivityRemittance.create_filled(payable_parts_none)

    def test_create_filled__one_payable_part_one_activity_registration(self):
        payable_part: ActivityPayablePart = baker.make_recipe(payable_part_with_unique_activity)
        payable_parts_one: QuerySet[ActivityPayablePart] = ActivityPayablePart.objects.all()

        activity_remittance: ActivityRemittance = ActivityRemittance.create_filled(payable_parts_one)

        self.assertEqual(activity_remittance.name, payable_part.name)
        self.assertIsNotNone(activity_remittance.payable_parts)
        self.assertEqual(list(activity_remittance.payable_parts.all()), list([payable_part]))
