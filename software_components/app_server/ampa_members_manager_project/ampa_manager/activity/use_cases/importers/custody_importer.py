from typing import Optional

from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.activity.use_cases.importers.base_importer import BaseImporter
from ampa_manager.activity.use_cases.importers.import_excel_result import ImportExcelResult
from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult
from ampa_manager.activity.use_cases.importers.row import Row
from ampa_manager.activity.use_cases.old_importers.custody_registration_importer import CustodyRegistrationImporter
from ampa_manager.activity.use_cases.importers.excel_data_extractor import ExcelDataExtractor
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.parent import Parent

from ampa_manager.family.use_cases.importers.family_holders_consolidator import FamilyHoldersConsolidator
from ampa_manager.utils.fields_formatters import FieldsFormatters


class CustodyImporter(BaseImporter):
    SHEET_NUMBER = 0
    FIRST_ROW_INDEX = 2

    LABEL_ASSISTED_DAYS = _('Assisted days in the selected edition')

    COLUMNS_TO_IMPORT = [
        [0, FieldsFormatters.format_email, BaseImporter.KEY_FAMILY_EMAIL, BaseImporter.LABEL_FAMILY_EMAIL],
        [1, FieldsFormatters.format_name, BaseImporter.KEY_PARENT_NAME_AND_SURNAMES,
         BaseImporter.LABEL_PARENT_NAME_AND_SURNAMES],
        [2, FieldsFormatters.format_phone, BaseImporter.KEY_PARENT_PHONE_NUMBER,
         BaseImporter.LABEL_PARENT_PHONE_NUMBER],
        [3, FieldsFormatters.format_email, BaseImporter.KEY_PARENT_EMAIL, BaseImporter.LABEL_PARENT_EMAIL],
        [4, FieldsFormatters.format_iban, BaseImporter.KEY_BANK_ACCOUNT_IBAN, BaseImporter.LABEL_BANK_ACCOUNT_IBAN],
        [5, FieldsFormatters.format_name, BaseImporter.KEY_CHILD_NAME, BaseImporter.LABEL_CHILD_NAME],
        [6, FieldsFormatters.format_name, BaseImporter.KEY_FAMILY_SURNAMES, BaseImporter.LABEL_CHILD_SURNAMES],
        [7, FieldsFormatters.format_integer, BaseImporter.KEY_CHILD_YEAR_OF_BIRTH,
         BaseImporter.LABEL_CHILD_YEAR_OF_BIRTH],
        [8, FieldsFormatters.format_level, BaseImporter.KEY_CHILD_LEVEL, BaseImporter.LABEL_CHILD_LEVEL],
        [9, FieldsFormatters.format_integer, BaseImporter.KEY_ASSISTED_DAYS, LABEL_ASSISTED_DAYS],
    ]

    def __init__(self, excel_content, custody_edition: CustodyEdition):
        self.excel_content = excel_content
        self.custody_edition = custody_edition
        self.rows = self.import_custody()

    def import_custody(self) -> ImportExcelResult:
        rows: list[Row] = ExcelDataExtractor(self.excel_content, self.SHEET_NUMBER, self.FIRST_ROW_INDEX,
                                             self.COLUMNS_TO_IMPORT).extract()

        for row in rows:
            self.import_row(row)

        return ImportExcelResult(rows)

    def import_row(self, row: Row):
        if row.any_error:
            return

        try:
            family: Family = self.import_family(row)
            if not family:
                return

            child: Child = self.import_child(row, family)
            if not child:
                return

            parent: Parent = self.import_parent(row, family)
            if row.any_error:
                return

            holder: Optional[Holder] = None
            if parent:
                holder = self.import_bank_account_and_holder(row, parent)

            FamilyHoldersConsolidator(family).consolidate()
            if not family.custody_holder:
                row.set_error('Missing bank account')
                return

            self.import_custody_registration(row, self.custody_edition, holder, child)

        except Exception as e:
            row.error = str(e)

    def import_custody_registration(self, row: Row, edition: CustodyEdition, holder: Holder, child: Child):
        assisted_days = row.get_value(self.KEY_ASSISTED_DAYS)

        result: ImportModelResult = CustodyRegistrationImporter(
            edition=edition,
            holder=holder,
            child=child,
            assisted_days=assisted_days).import_registration()

        row.add_imported_model_result(result)

        return result.instance
