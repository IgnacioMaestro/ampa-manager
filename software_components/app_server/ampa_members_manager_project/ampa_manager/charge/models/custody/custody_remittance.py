from __future__ import annotations

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from .custody_remittance_manager import CustodyRemittanceManager
from ..nameable_with_date import NameableWithDate


class CustodyRemittance(NameableWithDate, models.Model):
    custody_editions = models.ManyToManyField(
        to=CustodyEdition, verbose_name=_("CustodyEditions"), related_name="custody_remittance")

    objects = CustodyRemittanceManager()

    class Meta:
        verbose_name = _('Custody remittance')
        verbose_name_plural = _('Custody remittances')
        db_table = 'custody_remittance'

    def __str__(self) -> str:
        return self.name_with_date

    def get_admin_url(self):
        return reverse('admin:%s_%s_change' % (self._meta.app_label, self._meta.model_name), args=[self.id])
