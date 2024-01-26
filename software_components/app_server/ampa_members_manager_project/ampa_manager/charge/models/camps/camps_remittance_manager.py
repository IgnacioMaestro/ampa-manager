from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import transaction
from django.db.models import Manager, QuerySet
from django.utils import timezone

from ampa_manager.activity.models.camps.camps_edition import CampsEdition
from ampa_manager.charge.no_camps_edition_error import NoCampsEditionError

if TYPE_CHECKING:
    from ampa_manager.charge.models.camps.camps_remittance import CampsRemittance


class CampsRemittanceManager(Manager):
    def create_filled(self, camps_editions: QuerySet[CampsEdition]) -> CampsRemittance:
        if not camps_editions.exists():
            raise NoCampsEditionError

        with transaction.atomic():
            camps_remittance: CampsRemittance = self.create()
            camps_remittance.camps_editions.set(camps_editions)
            return camps_remittance

    def paid_on_current_year(self) -> QuerySet:
        return self.filter(payment_date__year=timezone.now().year)
