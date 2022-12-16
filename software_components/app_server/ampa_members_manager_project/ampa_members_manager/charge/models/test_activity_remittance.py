from django.db.models import QuerySet
from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.activity.models.activity_period import ActivityPeriod
from ampa_members_manager.charge.models.activity_remittance import ActivityRemittance
from ampa_members_manager.charge.no_activity_period_error import NoActivityPeriodError


class TestActivityRemittance(TestCase):
    def test_create_filled_no_activity_period(self):
        activity_periods_none: QuerySet[ActivityPeriod] = ActivityPeriod.objects.none()
        with self.assertRaises(NoActivityPeriodError):
            ActivityRemittance.create_filled(activity_periods_none)

    def test_create_filled__one_activity_period(self):
        activity_period: ActivityPeriod = baker.make('ActivityPeriod')
        activity_periods_one: QuerySet[ActivityPeriod] = ActivityPeriod.objects.all()

        activity_remittance: ActivityRemittance = ActivityRemittance.create_filled(activity_periods_one)

        self.assertEqual(activity_remittance.name, activity_period.name)
        self.assertIsNotNone(activity_remittance.activity_periods)
        self.assertEqual(list(activity_remittance.activity_periods.all()), list([activity_period]))
