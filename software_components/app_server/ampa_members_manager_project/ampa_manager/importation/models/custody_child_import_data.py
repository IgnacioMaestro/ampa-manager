from django.db import models
from django.utils.translation import gettext_lazy as _

from ampa_manager.importation.models.child_with_surnames_import_data import ChildWithSurnamesImportData


class CustodyChildImportData(ChildWithSurnamesImportData):
    days_attended = models.PositiveIntegerField(verbose_name=_("Days attended"))

    class Meta:
        abstract = True
        verbose_name = _('Custody child import data')
        verbose_name_plural = _('Custody child import data')
