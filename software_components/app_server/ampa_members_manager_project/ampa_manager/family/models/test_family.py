from typing import List

from django.test import TestCase
from model_bakery import baker
from django.utils.translation import gettext_lazy as _

from .bank_account.bank_account import BankAccount
from .family import Family
from .holder.holder import Holder
from ...baker_recipes import bank_account_recipe


class TestFamily(TestCase):

    def test_create_unique_surnames(self):
        baker.make('Family')
        Family.objects.create(surnames="surnames")

    def test_str_no_children(self):
        family: Family = baker.make('Family')
        self.assertEqual(
            str(family),
            str(family.surnames) + ": " + family.parents_names + " (" + _('No children') + ") " + str(family.id))

    def test_str_with_children(self):
        family: Family = baker.make('Family')
        baker.make('Child', family=family)
        self.assertEqual(
            str(family),
            str(family.surnames) + ": " + family.parents_names + " (" + family.children_names + ") " + str(family.id))

    def test_all_families_no_families(self):
        self.assertQuerysetEqual(Family.all_families(), Family.objects.none())

    def test_all_families_one_family(self):
        family: Family = baker.make('Family')
        self.assertQuerysetEqual(Family.all_families(), [family])

    def test_all_families_more_than_one_family(self):
        families: List[Family] = baker.make('Family', _quantity=3)
        self.assertListEqual(list(Family.all_families()), families)

    def test_all_families_with_holder_no_families(self):
        self.assertQuerysetEqual(Family.objects.with_membership_holder(), Family.objects.none())

    def test_all_families_with_holder_one_family(self):
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        holder: Holder = baker.make('Holder', bank_account=bank_account)
        family: Family = baker.make('Family', membership_holder=holder)
        self.assertQuerysetEqual(Family.objects.with_membership_holder(), [family])

    def test_all_families_with_bank_account_more_than_one_family(self):
        holder: Holder = baker.make('Holder')
        families: List[Family] = baker.make('Family', _quantity=3)
        families[0].membership_holder = holder
        families[0].save()
        families[1].membership_holder = holder
        families[1].save()

        self.assertEqual(len(Family.objects.with_membership_holder()), 2)
