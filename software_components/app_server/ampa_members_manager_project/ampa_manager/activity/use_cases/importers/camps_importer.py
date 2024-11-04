from typing import Optional

from ampa_manager.activity.models.camps.camps_edition import CampsEdition
from ampa_manager.activity.models.camps.camps_registration import CampsRegistration
from ampa_manager.activity.use_cases.importers.base_importer import BaseImporter
from ampa_manager.activity.use_cases.importers.camps_registration_importer import CampsRegistrationImporter
from ampa_manager.activity.use_cases.importers.excel_column import ExcelColumn
from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult
from ampa_manager.activity.use_cases.importers.row import Row
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.parent import Parent
from ampa_manager.family.use_cases.importers.family_holders_consolidator import FamilyHoldersConsolidator


class CampsImporter(BaseImporter):
    SHEET_NUMBER = 0
    FIRST_ROW_INDEX = 2

    COLUMNS_TO_IMPORT = [
        ExcelColumn(0, BaseImporter.family_email, compulsory=True),
        ExcelColumn(1, BaseImporter.parent_1_name_and_surnames, compulsory=False),
        ExcelColumn(2, BaseImporter.parent_1_phone_number, compulsory=False),
        ExcelColumn(3, BaseImporter.parent_1_email, compulsory=False),
        ExcelColumn(4, BaseImporter.bank_account_iban, compulsory=False),
        ExcelColumn(5, BaseImporter.child_1_name, compulsory=True),
        ExcelColumn(6, BaseImporter.family_surnames, compulsory=False),
        ExcelColumn(7, BaseImporter.child_1_year_of_birth, compulsory=False),
        ExcelColumn(8, BaseImporter.child_1_level, compulsory=False),
    ]

    def __init__(self, excel_content: bytes, camps_edition: CampsEdition):
        self.camps_edition: CampsEdition = camps_edition
        super().__init__(excel_content)

    def process_row(self, row: Row):
        if row.any_error or row.is_empty:
            return

        try:
            family: Family = self.import_family(row)
            if not family:
                return

            child: Child = self.import_child(row, family, compulsory=True)
            if not child:
                return

            parent: Parent = self.import_parent(row, family, compulsory=False)
            if row.any_error:
                return

            if parent:
                holder: Optional[Holder] = self.import_bank_account_and_holder(row, parent)
                if holder:
                    family.update_camps_holder(holder)

            FamilyHoldersConsolidator(family).consolidate()

            if not family.update_camps_holder:
                row.set_error('Missing bank account')
                return

            self.import_camps_registration(row, self.camps_edition, family.camps_holder, child)

        except Exception as e:
            row.error = str(e)

    def import_camps_registration(self, row: Row, edition: CampsEdition, holder: Holder,
                                  child: Child) -> CampsRegistration:
        assisted_days = row.get_value(self.KEY_ASSISTED_DAYS)

        result: ImportModelResult = CampsRegistrationImporter(
            edition=edition, holder=holder, child=child).import_registration()

        row.add_imported_model_result(result)

        return result.instance
