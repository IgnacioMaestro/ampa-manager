from django.db import models
from django.utils.translation import gettext_lazy as _

from ampa_manager.importation.models.custody_child_import_data import CustodyChildImportData
from ampa_manager.importation.models.custody_importation import CustodyImportation
from ampa_manager.importation.models.holder_import_data import HolderImportData


class CustodyImportationRow(CustodyChildImportData, HolderImportData):
    importation = models.ForeignKey(to=CustodyImportation, on_delete=models.CASCADE, verbose_name=_("Importation"))
    row = models.PositiveIntegerField(verbose_name=_("Row"))

    class Meta:
        verbose_name = _("Custody importation row")
        verbose_name_plural = _("Custody importation rows")
        db_table = 'custody_importation_row'
        constraints = [
            models.UniqueConstraint(fields=["importation", "row"], name="unique_importation_row")
        ]
