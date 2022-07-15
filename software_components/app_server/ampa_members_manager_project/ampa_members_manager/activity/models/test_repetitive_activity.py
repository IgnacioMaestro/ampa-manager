from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.activity.models.repetitive_activity import RepetitiveActivity
from ampa_members_manager.activity.models.single_activity import SingleActivity


class TestRepetitiveActivity(TestCase):
    def test_str(self):
        repetitive_activity: RepetitiveActivity = baker.make('RepetitiveActivity')
        self.assertEqual(str(repetitive_activity), repetitive_activity.name)

    def test_all_same_repetitive_activity_one_single_activity(self):
        baker.make('SingleActivity')
        same: bool = RepetitiveActivity.all_same_repetitive_activity(SingleActivity.objects.all())
        self.assertTrue(same)

    def test_all_same_repetitive_activity_two_single_activity_with_same_repetitive_activity(self):
        single_activity: SingleActivity = baker.make('SingleActivity')
        baker.make('RepetitiveActivity', single_activities=[single_activity])
        baker.make('RepetitiveActivity', single_activities=[single_activity])
        same: bool = RepetitiveActivity.all_same_repetitive_activity(SingleActivity.objects.all())
        self.assertTrue(same)

    def test_all_same_repetitive_activity_two_single_activity_with_different_repetitive_activity(self):
        single_activity: SingleActivity = baker.make('SingleActivity')
        other_single_activity: SingleActivity = baker.make('SingleActivity')
        baker.make('RepetitiveActivity', single_activities=[single_activity])
        baker.make('RepetitiveActivity', single_activities=[other_single_activity])
        same: bool = RepetitiveActivity.all_same_repetitive_activity(SingleActivity.objects.all())
        self.assertFalse(same)
