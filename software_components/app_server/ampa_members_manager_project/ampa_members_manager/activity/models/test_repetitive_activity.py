from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.activity.models.repetitive_activity import RepetitiveActivity


class TestRepetitiveActivity(TestCase):
    def test_str(self):
        repetitive_activity: RepetitiveActivity = baker.make('RepetitiveActivity')
        self.assertEqual(str(repetitive_activity), repetitive_activity.name)
