from typing import List

from django.db import IntegrityError
from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.family.models.family import Family


class TestFamily(TestCase):
    def test_create_no_unique_email(self):
        family: Family = baker.make('Family')
        with self.assertRaises(IntegrityError):
            Family.objects.create(
                first_surname="first_surname", second_surname="second_surname", email=family.email)

    def test_create_unique_email_and_unique_surnames(self):
        baker.make('Family')
        Family.objects.create(first_surname="first_surname", second_surname="second_surname", email="unique_email")

    def test_create_no_unique_surnames(self):
        family: Family = baker.make('Family')
        with self.assertRaises(IntegrityError):
            Family.objects.create(
                first_surname=family.first_surname, second_surname=family.second_surname,
                email="unique_email")

    def test_str(self):
        family: Family = baker.make('Family')
        self.assertEqual(str(family), "{} {}".format(family.first_surname, family.second_surname))

    def test_all_families_no_families(self):
        self.assertQuerysetEqual(Family.all_families(), Family.objects.none())

    def test_all_families_one_family(self):
        family: Family = baker.make('Family')
        self.assertQuerysetEqual(Family.all_families(), [family])

    def test_all_families_more_than_one_family(self):
        families: List[Family] = baker.make('Family', _quantity=3)
        self.assertListEqual(list(Family.all_families()), families)
