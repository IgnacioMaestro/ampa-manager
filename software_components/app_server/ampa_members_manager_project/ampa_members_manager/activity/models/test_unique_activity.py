from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.activity.models.unique_activity import UniqueActivity


class TestUniqueActivity(TestCase):
    def test_str(self):
        unique_activity: UniqueActivity = baker.make('UniqueActivity')
        self.assertEqual(str(unique_activity), unique_activity.name)
