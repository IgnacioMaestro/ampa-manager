from django.core.exceptions import ValidationError
from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.family.models.child import Child


class TestChild(TestCase):
    def test_str(self):
        child: Child = baker.make('Child')
        self.assertEqual(str(child), "{} {}".format(child.name, str(child.family)))

    def test_year_lower_minimal(self):
        with self.assertRaises(ValidationError):
            child: Child = Child(name='name_min', year_of_birth=999, family=baker.make('Family'))
            child.full_clean()

    def test_year_major_maximum(self):
        with self.assertRaises(ValidationError):
            child: Child = Child(name='name_min', year_of_birth=3001, family=baker.make('Family'))
            child.full_clean()

    def test_year_on_range(self):
        child: Child = Child(name='name_min', year_of_birth=2022, family=baker.make('Family'))
        child.full_clean()
