from __future__ import annotations

from django.db import models, transaction
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ..nameable_with_date import NameableWithDate
from ...no_custody_edition_error import NoCustodyEditionError


class CustodyRemittance(NameableWithDate, models.Model):
    custody_editions = models.ManyToManyField(
        to=CustodyEdition, verbose_name=_("CustodyEditions"), related_name="custody_remittance")

    class Meta:
        verbose_name = _('Custody remittance')
        verbose_name_plural = _('Custody remittances')
        db_table = 'custody_remittance'

    def __str__(self) -> str:
        return self.name_with_date

    def get_admin_url(self):
        return reverse('admin:%s_%s_change' % (self._meta.app_label, self._meta.model_name), args=[self.id])

    @classmethod
    def create_filled(cls, custody_editions: QuerySet[CustodyEdition]) -> CustodyRemittance:
        if not custody_editions.exists():
            raise NoCustodyEditionError

        with transaction.atomic():
            custody_remittance: CustodyRemittance = CustodyRemittance.objects.create()
            custody_remittance.custody_editions.set(custody_editions)
            return custody_remittance
