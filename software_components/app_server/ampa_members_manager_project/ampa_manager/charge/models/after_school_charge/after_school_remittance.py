from __future__ import annotations

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from .after_school_remittance_manager import AfterSchoolRemittanceManager
from ..nameable_with_date import NameableWithDate


class AfterSchoolRemittance(NameableWithDate, models.Model):
    after_school_editions = models.ManyToManyField(
        to=AfterSchoolEdition, verbose_name=_("AfterSchoolEditions"), related_name="after_school_remittance")

    objects = AfterSchoolRemittanceManager()

    class Meta:
        verbose_name = _('After-school remittance')
        verbose_name_plural = _('After-school remittances')
        db_table = 'after_school_remittance'

    def __str__(self) -> str:
        return self.name_with_date

    def get_admin_url(self):
        return reverse('admin:%s_%s_change' % (self._meta.app_label, self._meta.model_name), args=[self.id])
