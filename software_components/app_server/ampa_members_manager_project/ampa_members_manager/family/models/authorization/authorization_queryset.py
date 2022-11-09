from django.db.models import QuerySet

from ampa_members_manager.family.models.bank_account.bank_account import BankAccount


class AuthorizationQueryset(QuerySet):
    def of_bank_account(self, bank_account: BankAccount) -> QuerySet:
        return self.filter(bank_account=bank_account)

    def authorization_with_highest_number(self, year: int):
        return self.filter(year=year).order_by('number').first()
