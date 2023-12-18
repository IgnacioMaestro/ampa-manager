from django.db import models
from django.utils.translation import gettext_lazy as _

from ampa_manager.importation.models.child_import_data import ChildImportData


class ChildWithSurnamesImportData(ChildImportData):
    surnames = models.CharField(max_length=500, verbose_name=_("Surnames"))

    class Meta:
        abstract = True
        verbose_name = _("Child with surnames")
        verbose_name_plural = _("Children with surnames")
