from __future__ import annotations

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.camps.camps_edition import CampsEdition
from .camps_remittance_manager import CampsRemittanceManager
from ..nameable_with_date import NameableWithDate


class CampsRemittance(NameableWithDate, models.Model):
    camps_editions = models.ManyToManyField(
        to=CampsEdition, verbose_name=_("CampsEdition"), related_name="camps_remittance")

    objects = CampsRemittanceManager()

    class Meta:
        verbose_name = _('Camps remittance')
        verbose_name_plural = _('Camps remittances')
        db_table = 'camps_remittance'

    def __str__(self) -> str:
        return self.name_with_date

    def get_admin_url(self):
        return reverse('admin:%s_%s_change' % (self._meta.app_label, self._meta.model_name), args=[self.id])
