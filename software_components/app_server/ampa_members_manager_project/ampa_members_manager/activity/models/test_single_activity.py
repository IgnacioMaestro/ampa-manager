from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.activity.models.single_activity import SingleActivity


class TestSingleActivity(TestCase):
    def test_str(self):
        single_activity: SingleActivity = baker.make('SingleActivity')
        self.assertEqual(str(single_activity), single_activity.name)
