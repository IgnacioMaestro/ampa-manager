from django.db import IntegrityError
from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.family.models.parent import Parent


class TestParent(TestCase):
    def test_str(self):
        parent: Parent = baker.make('Parent')
        self.assertEqual(str(parent), "{} {} {}".format(parent.name, parent.first_surname, parent.second_surname))

    def test_create_no_unique_name_surname_family(self):
        parent: Parent = baker.make('Parent')
        with self.assertRaises(IntegrityError):
            Parent.objects.create(
                name=parent.name, first_surname=parent.first_surname, second_surname=parent.second_surname)

    def test_create_unique_name_surname_family(self):
        baker.make('Parent')
        Parent.objects.create(name="name", first_surname="first_surname", second_surname="second_surname")
