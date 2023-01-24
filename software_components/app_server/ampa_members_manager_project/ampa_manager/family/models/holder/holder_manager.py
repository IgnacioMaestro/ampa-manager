from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Manager

from ampa_manager.academic_course.models.active_course import ActiveCourse
from ..bank_account.bank_account import BankAccount
from ..parent import Parent

if TYPE_CHECKING:
    from .holder import Holder


class HolderManager(Manager):
    def next_order_for_year(self, year: int) -> int:
        holder: Holder = self.authorization_with_highest_order(year=year)
        if not holder:
            return 1
        return holder.authorization_order + 1

    def create_for_active_course(self, parent: Parent, bank_account: BankAccount) -> Holder:
        academic_course = ActiveCourse.load()
        return self.create(parent=parent, bank_account=bank_account,
                           authorization_order=self.next_order_for_year(academic_course.initial_year),
                           authorization_year=academic_course.initial_year)
