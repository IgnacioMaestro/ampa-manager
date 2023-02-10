from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import transaction
from django.db.models import Manager, QuerySet

from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ...no_after_school_edition_error import NoAfterSchoolEditionError

if TYPE_CHECKING:
    from .after_school_remittance import AfterSchoolRemittance


class AfterSchoolRemittanceManager(Manager):
    def create_filled(self, after_school_editions: QuerySet[AfterSchoolEdition]) -> AfterSchoolRemittance:
        if not after_school_editions.exists():
            raise NoAfterSchoolEditionError

        with transaction.atomic():
            after_school_remittance: AfterSchoolRemittance = self.create()
            after_school_remittance.after_school_editions.set(after_school_editions)
            return after_school_remittance
