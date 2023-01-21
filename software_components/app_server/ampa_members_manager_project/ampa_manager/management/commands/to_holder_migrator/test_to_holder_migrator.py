from django.test import TestCase
from model_bakery import baker

from ampa_manager.baker_recipes import bank_account_recipe
from ampa_manager.family.models.authorization.authorization_old import AuthorizationOld
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.parent import Parent
from .to_holder_migrator import ToHolderMigrator


class TestToHolderMigrator(TestCase):
    def test_migrate_no_linked_bank_account(self):
        # Arrange
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        authorization_old: AuthorizationOld = baker.make('AuthorizationOld', bank_account=bank_account)
        parent: Parent = bank_account.owner

        # Act
        ToHolderMigrator.migrate()

        # Assert
        self.assertEqual(AuthorizationOld.objects.count(), 0)
        self.assert_one_holder(authorization_old, bank_account, parent)

    def test_migrate_linked_bank_account(self):
        # Arrange
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        family: Family = baker.make('Family', default_bank_account=bank_account)
        authorization_old: AuthorizationOld = baker.make('AuthorizationOld', bank_account=bank_account)
        parent: Parent = bank_account.owner
        family.parents.add(parent)

        # Act
        ToHolderMigrator.migrate()

        # Assert
        self.assertEqual(AuthorizationOld.objects.count(), 0)
        holder: Holder = self.assert_one_holder(authorization_old, bank_account, parent)
        family.refresh_from_db()
        self.assertEqual(family.default_holder, holder)

    def assert_one_holder(
            self, authorization_old: AuthorizationOld, bank_account: BankAccount, parent: Parent) -> Holder:
        self.assertEqual(Holder.objects.count(), 1)
        holder: Holder = Holder.objects.first()
        self.assertEqual(holder.parent, parent)
        self.assertEqual(holder.bank_account, bank_account)
        self.assertEqual(holder.full_number, authorization_old.full_number)
        self.assertEqual(holder.sign_date, authorization_old.sign_date)
        self.assertEqual(holder.state, authorization_old.state)
        self.assertFalse(holder.document)
        return holder
