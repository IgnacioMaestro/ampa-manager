from typing import Optional

from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.activity.use_cases.importers.custody_registration_importer import CustodyRegistrationImporter
from ampa_manager.activity.use_cases.importers.excel_manager import ExcelManager, Row, BaseImporter, ImportSummary
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.parent import Parent
from ampa_manager.utils.excel.import_model_result import ImportModelResult
from ampa_manager.utils.fields_formatters import FieldsFormatters


class CustodyImporter(BaseImporter):
    SHEET_NUMBER = 0
    FIRST_ROW_INDEX = 2

    LABEL_ASSISTED_DAYS = _('Assisted days in the selected edition')

    COLUMNS_TO_IMPORT = [
        [0, FieldsFormatters.clean_email, BaseImporter.KEY_FAMILY_EMAIL, BaseImporter.LABEL_FAMILY_EMAIL],
        [1, FieldsFormatters.clean_name, BaseImporter.KEY_PARENT_NAME_AND_SURNAMES, BaseImporter.LABEL_PARENT_NAME_AND_SURNAMES],
        [2, FieldsFormatters.clean_phone, BaseImporter.KEY_PARENT_PHONE_NUMBER, BaseImporter.LABEL_PARENT_PHONE_NUMBER],
        [3, FieldsFormatters.clean_email, BaseImporter.KEY_PARENT_EMAIL, BaseImporter.LABEL_PARENT_EMAIL],
        [4, FieldsFormatters.clean_iban, BaseImporter.KEY_BANK_ACCOUNT_IBAN, BaseImporter.LABEL_BANK_ACCOUNT_IBAN],
        [5, FieldsFormatters.clean_name, BaseImporter.KEY_CHILD_NAME, BaseImporter.LABEL_CHILD_NAME],
        [6, FieldsFormatters.clean_name, BaseImporter.KEY_CHILD_SURNAMES, BaseImporter.LABEL_CHILD_SURNAMES],
        [7, FieldsFormatters.clean_integer, BaseImporter.KEY_CHILD_YEAR_OF_BIRTH, BaseImporter.LABEL_CHILD_YEAR_OF_BIRTH],
        [8, FieldsFormatters.clean_level, BaseImporter.KEY_CHILD_LEVEL, BaseImporter.LABEL_CHILD_LEVEL],
        [9, FieldsFormatters.clean_integer, BaseImporter.KEY_ASSISTED_DAYS, LABEL_ASSISTED_DAYS],
    ]

    def __init__(self, excel_content, custody_edition: CustodyEdition):
        self.excel_content = excel_content
        self.custody_edition = custody_edition
        self.rows = self.import_custody()

    def import_custody(self) -> ImportSummary:
        manager = ExcelManager(self.excel_content, self.SHEET_NUMBER, self.FIRST_ROW_INDEX, self.COLUMNS_TO_IMPORT)

        for row in manager.rows:
            self.import_row(row)

        return ImportSummary(manager.rows)

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
            self.consolidate_family_holders(family)

            if not family.custody_holder:
                row.set_error('Missing bank account')
                return

            self.import_custody_registration(row, self.custody_edition, holder, child)

        except Exception as e:
            row.error = str(e)

    def import_custody_registration(self, row: Row, custody_edition, holder: Holder, child: Child):
        assisted_days = row.get_value(self.KEY_ASSISTED_DAYS)

        imported_model: ImportModelResult = CustodyRegistrationImporter.import_registration(
            custody_edition=custody_edition,
            holder=holder,
            child=child,
            assisted_days=assisted_days)

        row.add_imported_model(imported_model)
