from typing import Optional

from ampa_manager.activity.use_cases.importers.base_importer import BaseImporter
from ampa_manager.activity.use_cases.importers.excel_column import ExcelColumn
from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult
from ampa_manager.activity.use_cases.importers.row import Row
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.membership import Membership
from ampa_manager.family.models.parent import Parent
from ampa_manager.family.use_cases.importers.family_holders_consolidator import FamilyHoldersConsolidator
from ampa_manager.family.use_cases.importers.membership_importer import MembershipImporter


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

    def process_row(self, row: Row):
        if row.any_error or row.is_empty:
            return

        try:
            family: Family = self.import_family(row)
            if not family:
                return

            child1: Child = self.import_child(row, family, compulsory=True, child_number=1)
            if not child1:
                return

            self.import_child(row, family, compulsory=False, child_number=2)
            if row.any_error:
                return

            self.import_child(row, family, compulsory=False, child_number=3)
            if row.any_error:
                return

            self.import_child(row, family, compulsory=False, child_number=4)
            if row.any_error:
                return

            parent1: Parent = self.import_parent(row, family, compulsory=True, parent_number=1)
            if row.any_error:
                return

            if parent1:
                holder: Optional[Holder] = self.import_bank_account_and_holder(row, parent1)
                if holder:
                    family.update_membership_holder(holder)

            self.import_parent(row, family, compulsory=False, parent_number=2)
            if row.any_error:
                return

            FamilyHoldersConsolidator(family).consolidate()

            if not family.membership_holder:
                row.set_error('Missing bank account')
                return

            self.import_membership(row, family)

        except Exception as e:
            row.error = str(e)

    @classmethod
    def import_membership(cls, row: Row, family: Family) -> Membership:
        result: ImportModelResult = MembershipImporter(family=family).import_membership()
        row.add_imported_model_result(result)
        return result.instance
