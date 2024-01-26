from django.db import models
from django.utils.translation import gettext_lazy as _

from ampa_manager.importation.models.custody_child_import_data import CustodyChildImportData
from ampa_manager.importation.models.custody_importation import CustodyImportation
from ampa_manager.importation.models.holder_import_data import HolderImportData
from ampa_manager.importation.models.levels import Levels
from ampa_manager.importation.use_cases.custody_importer.rows_importer.custody_import_row import CustodyImportRow


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

    @classmethod
    def create_from_custody_import_row(cls, custody_import_row: CustodyImportRow, importation: CustodyImportation):
        return cls.objects.create(
            importation=importation, row=custody_import_row.row,
            days_attended=custody_import_row.days_attended,
            surnames=custody_import_row.child_surnames,
            name=custody_import_row.child_name,
            year_of_birth=custody_import_row.child_year_of_birth,
            level=Levels.obtain_from_level_constant(custody_import_row.child_level),
            iban=custody_import_row.holder_import_data.iban,
            name_and_surnames=custody_import_row.holder_import_data.parent_import_data.holder_name_and_surnames,
            phone_number=custody_import_row.holder_import_data.parent_import_data.phone_number,
            email=custody_import_row.holder_import_data.parent_import_data.email)
