from django.db.models import QuerySet

from ..bank_account.bank_account import BankAccount


class HolderQuerySet(QuerySet):
    def of_bank_account(self, bank_account: BankAccount) -> QuerySet:
        return self.filter(bank_account=bank_account)

    def authorization_with_highest_number(self, year: int):
        return self.filter(authorization_year=year).order_by('number').first()

    def authorization_with_highest_order(self, year: int):
        return self.filter(authorization_year=year).order_by('authorization_order').last()
