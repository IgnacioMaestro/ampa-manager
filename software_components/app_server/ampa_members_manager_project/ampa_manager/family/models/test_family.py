from typing import List

from django.test import TestCase
from model_bakery import baker

from .family import Family
from .holder.holder import Holder


class TestFamily(TestCase):

    def test_create_unique_surnames(self):
        baker.make('Family')
        Family.objects.create(surnames="surnames")

    def test_str(self):
        family: Family = baker.make('Family')
        self.assertEqual(str(family), str(family.surnames))

    def test_all_families_no_families(self):
        self.assertQuerysetEqual(Family.all_families(), Family.objects.none())

    def test_all_families_one_family(self):
        family: Family = baker.make('Family')
        self.assertQuerysetEqual(Family.all_families(), [family])

    def test_all_families_more_than_one_family(self):
        families: List[Family] = baker.make('Family', _quantity=3)
        self.assertListEqual(list(Family.all_families()), families)

    def test_all_families_with_holder_no_families(self):
        self.assertQuerysetEqual(Family.objects.with_default_holder(), Family.objects.none())

    def test_all_families_with_holder_one_family(self):
        holder: Holder = baker.make('Holder')
        family: Family = baker.make('Family', default_holder=holder)
        self.assertQuerysetEqual(Family.objects.with_default_holder(), [family])

    def test_all_families_with_bank_account_more_than_one_family(self):
        holder: Holder = baker.make('Holder')
        families: List[Family] = baker.make('Family', _quantity=3)
        families[0].default_holder = holder
        families[0].save()
        families[1].default_holder = holder
        families[1].save()

        self.assertEqual(len(Family.objects.with_default_holder()), 2)
