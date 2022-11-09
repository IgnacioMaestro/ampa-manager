from __future__ import annotations
from typing import TYPE_CHECKING

from django.db.models import Manager

from ampa_members_manager.family.models.bank_account.bank_account import BankAccount

if TYPE_CHECKING:
    from ampa_members_manager.family.models.authorization.authorization import Authorization


class AuthorizationManager(Manager):
    def create_next_authorization(self, year: int, bank_account: BankAccount) -> Authorization:
        number = self.next_number_for_year(year)
        return self.create(year=year, number=str(number), bank_account=bank_account)

    def next_number_for_year(self, year: int) -> int:
        authorization: Authorization = self.authorization_with_highest_number(year=year)
        if not authorization:
            return 1
        return int(authorization.number) + 1
