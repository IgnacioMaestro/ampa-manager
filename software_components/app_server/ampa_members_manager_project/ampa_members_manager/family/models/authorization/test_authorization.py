import phonenumbers
from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.family.models.authorization.authorization import Authorization
from ampa_members_manager.family.models.bank_account.bank_account import BankAccount
from ampa_members_manager.family.models.parent import Parent


class TestAuthorization(TestCase):
    def test_str(self):
        owner: Parent = baker.make('Parent', phone_number=phonenumbers.parse("695715902", 'ES'))
        bank_account: BankAccount = baker.make(
            'BankAccount', swift_bic="BASKES2BXXX", iban="ES60 0049 1500 0512 3456 7892", owner=owner)
        authorization: Authorization = baker.make('Authorization', bank_account=bank_account)
        self.assertEqual(
            str(authorization),
            f'{authorization.year}/{authorization.number}-{str(authorization.bank_account)}')
