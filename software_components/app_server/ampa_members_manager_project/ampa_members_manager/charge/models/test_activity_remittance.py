from django.db.models import QuerySet
from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.activity.models.single_activity import SingleActivity
from ampa_members_manager.charge.models.activity_remittance import ActivityRemittance
from ampa_members_manager.charge.no_single_activity_error import NoSingleActivityError


class TestActivityRemittance(TestCase):
    def test_create_filled_charge_group_no_single_activity(self):
        single_activities_none: QuerySet[SingleActivity] = SingleActivity.objects.none()
        with self.assertRaises(NoSingleActivityError):
            ActivityRemittance.create_filled(single_activities_none)

    def test_create_filled_charge_group_one_single_activity_one_activity_registration(self):
        single_activity: SingleActivity = baker.make('SingleActivity')
        single_activities_one: QuerySet[SingleActivity] = SingleActivity.objects.all()
        charge_group: ActivityRemittance = ActivityRemittance.create_filled(single_activities_one)
        self.assertIsNotNone(charge_group.single_activities)
        self.assertEqual(list(charge_group.single_activities.all()), list([single_activity]))