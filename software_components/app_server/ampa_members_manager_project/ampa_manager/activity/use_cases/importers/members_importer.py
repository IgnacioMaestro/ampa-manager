from typing import Optional

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.activity.use_cases.importers.base_importer import BaseImporter
from ampa_manager.activity.use_cases.importers.excel_column import ExcelColumn
from ampa_manager.activity.use_cases.importers.excel_data_extractor_pandas import ExcelDataExtractorPandas
from ampa_manager.activity.use_cases.importers.import_excel_result import ImportExcelResult
from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult
from ampa_manager.activity.use_cases.importers.row import Row
from ampa_manager.activity.use_cases.old_importers.custody_registration_importer import CustodyRegistrationImporter
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.parent import Parent
from ampa_manager.family.use_cases.importers.family_holders_consolidator import FamilyHoldersConsolidator


class MembersImporter(BaseImporter):
    SHEET_NUMBER = 0
    FIRST_ROW_INDEX = 2

    COLUMNS_TO_IMPORT = [
        ExcelColumn(0, BaseImporter.family_email),
        ExcelColumn(1, BaseImporter.family_surnames),
        ExcelColumn(1, BaseImporter.parent_1_name_and_surnames),
        ExcelColumn(2, BaseImporter.parent_1_phone_number),
        ExcelColumn(3, BaseImporter.parent_1_email),
        ExcelColumn(4, BaseImporter.bank_account_iban),
        ExcelColumn(1, BaseImporter.parent_2_name_and_surnames),
        ExcelColumn(2, BaseImporter.parent_2_phone_number),
        ExcelColumn(3, BaseImporter.parent_2_email),
        ExcelColumn(5, BaseImporter.child_1_name),
        ExcelColumn(7, BaseImporter.child_1_year_of_birth),
        ExcelColumn(8, BaseImporter.child_1_level),
        ExcelColumn(5, BaseImporter.child_2_name),
        ExcelColumn(7, BaseImporter.child_2_year_of_birth),
        ExcelColumn(8, BaseImporter.child_2_level),
        ExcelColumn(5, BaseImporter.child_3_name),
        ExcelColumn(7, BaseImporter.child_3_year_of_birth),
        ExcelColumn(8, BaseImporter.child_3_level),
        ExcelColumn(5, BaseImporter.child_4_name),
        ExcelColumn(7, BaseImporter.child_4_year_of_birth),
        ExcelColumn(8, BaseImporter.child_4_level),
    ]

    def __init__(self, excel_content: bytes, custody_edition: CustodyEdition):
        self.excel_content: bytes = excel_content
        self.custody_edition: CustodyEdition = custody_edition

    def run(self) -> ImportExcelResult:
        rows: list[Row] = ExcelDataExtractorPandas(
            self.excel_content, self.SHEET_NUMBER, self.FIRST_ROW_INDEX, self.COLUMNS_TO_IMPORT).extract()

        for row in rows:
            self.process_row(row)

        return ImportExcelResult(rows)

    def process_row(self, row: Row):
        if row.any_error or row.is_empty:
            return

        try:
            family: Family = self.import_family(row)
            if not family:
                return

            child: Child = self.import_child(row, family)
            if not child:
                return

            parent: Parent = self.import_parent(row, family, False)
            if row.any_error:
                return

            if parent:
                holder: Optional[Holder] = self.import_bank_account_and_holder(row, parent)
                if holder:
                    family.update_custody_holder(holder)

            FamilyHoldersConsolidator(family).consolidate()

            if not family.custody_holder:
                row.set_error('Missing bank account')
                return

            self.import_custody_registration(row, self.custody_edition, family.custody_holder, child)

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
