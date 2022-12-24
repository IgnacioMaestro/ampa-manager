from django.test import TestCase
from model_bakery import baker

from ampa_manager.activity.models.activity import Activity


class TestActivity(TestCase):
    def test_str(self):
        activity: Activity = baker.make('Activity')
        self.assertEqual(str(activity), activity.name)
