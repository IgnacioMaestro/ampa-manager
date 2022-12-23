from django.test import TestCase
from model_bakery import baker

from ampa_manager.activity.models.after_school.after_school import AfterSchool


class TestAfterSchool(TestCase):
    def test_str(self):
        after_school: AfterSchool = baker.make('AfterSchool')
        self.assertEqual(str(after_school), after_school.name)
