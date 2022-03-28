from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.family.models.child import Child


class TestChild(TestCase):
    def test_str(self):
        child: Child = baker.make('Child')
        self.assertEqual(str(child), "{} {}".format(child.name, str(child.family)))
