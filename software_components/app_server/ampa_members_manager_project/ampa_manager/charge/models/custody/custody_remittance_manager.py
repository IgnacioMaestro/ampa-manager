from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import transaction
from django.db.models import Manager, QuerySet
from django.utils import timezone

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.charge.no_custody_edition_error import NoCustodyEditionError

if TYPE_CHECKING:
    from ampa_manager.charge.models.custody.custody_remittance import CustodyRemittance


class CustodyRemittanceManager(Manager):
    def create_filled(self, custody_editions: QuerySet[CustodyEdition]) -> CustodyRemittance:
        if not custody_editions.exists():
            raise NoCustodyEditionError

        with transaction.atomic():
            custody_remittance: CustodyRemittance = self.create()
            custody_remittance.custody_editions.set(custody_editions)
            return custody_remittance

    def paid_on_current_year(self) -> QuerySet[CustodyRemittance]:
        return self.filter(payment_date__year=timezone.now().year)
