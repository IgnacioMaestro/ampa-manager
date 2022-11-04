from django.db.models import QuerySet

from ampa_members_manager.family.models.bank_account.bank_account import BankAccount


class AuthorizationQueryset(QuerySet):
    def of_bank_account(self, bank_account: BankAccount):
        return self.filter(bank_account=bank_account)
