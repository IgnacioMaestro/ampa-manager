from typing import List, Final

from django.test import TestCase

from model_bakery import baker

from ampa_members_manager.activity_registration.models.activity_registration import ActivityRegistration
from ampa_members_manager.charge.models.charge import Charge
from ampa_members_manager.charge.models.charge_group import ChargeGroup
from ampa_members_manager.charge.receipt import Receipt
from ampa_members_manager.charge.remittance import Remittance
from ampa_members_manager.charge.use_cases.generate_remittance_from_charge_group.remittance_generator import \
    RemittanceGenerator
from ampa_members_manager.family.models.bank_account import BankAccount
from ampa_members_manager.tests.generator_adder import GeneratorAdder

GeneratorAdder.add_all()


class TestRemittanceGenerator(TestCase):
    remittance_name: str = 'Remittance Name'

    def test_generate_remittance_no_charge(self):
        charge_group: ChargeGroup = baker.make('ChargeGroup')

        remittance: Remittance = RemittanceGenerator(charge_group, name=self.remittance_name).generate()

        self.assertEqual(remittance.name, self.remittance_name)
        self.assertEqual(len(remittance.receipts), 0)

    def test_generate_remittance_one_charge(self):
        charge_group: ChargeGroup = baker.make('ChargeGroup')
        charge: Charge = baker.make('Charge', group=charge_group)
        bank_account: BankAccount = baker.make('BankAccount')
        activity_registration: ActivityRegistration = baker.make('ActivityRegistration', bank_account=bank_account)
        charge.activity_registrations.add(activity_registration)

        remittance: Remittance = RemittanceGenerator(charge_group, name=self.remittance_name).generate()

        self.assertEqual(remittance.name, self.remittance_name)
        self.assertEqual(len(remittance.receipts), 1)
        receipt: Receipt = remittance.receipts[0]
        self.assertEqual(receipt.amount, charge.amount)
        self.assertEqual(receipt.bank_account_owner, bank_account.owner.full_name)
        self.assertEqual(receipt.authorization, 'No authorization')
        self.assertEqual(receipt.iban, bank_account.iban)

    def test_generate_remittance_two_charges(self):
        charge_count: Final[int] = 2
        charge_group: ChargeGroup = baker.make('ChargeGroup')
        charges: List[Charge] = baker.make('Charge', _quantity=charge_count, group=charge_group)
        bank_account: BankAccount = baker.make('BankAccount')
        for charge in charges:
            activity_registration: ActivityRegistration = baker.make('ActivityRegistration', bank_account=bank_account)
            charge.activity_registrations.add(activity_registration)

        remittance: Remittance = RemittanceGenerator(charge_group, name=self.remittance_name).generate()

        self.assertEqual(remittance.name, self.remittance_name)
        self.assertEqual(len(remittance.receipts), charge_count)
