from typing import Optional

from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.activity.use_cases.importers.custody_registration_importer import CustodyRegistrationImporter
from ampa_manager.activity.use_cases.importers.excel_manager import ExcelManager, Row, BaseImporter
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.parent import Parent
from ampa_manager.utils.excel.import_model_result import ImportModelResult
from ampa_manager.utils.fields_formatters import FieldsFormatters
from ampa_manager.utils.fields_formatters_django import FieldsFormattersDjango


class CustodyImporter(BaseImporter):
    SHEET_NUMBER = 0
    FIRST_ROW_INDEX = 2

    LABEL_FAMILY_EMAIL = _('Family email')
    LABEL_PARENT_NAME_AND_SURNAMES = _('Parent name and surnames')
    LABEL_PARENT_PHONE_NUMBER = _('Parent phone number')
    LABEL_PARENT_EMAIL = _('Parent email')
    LABEL_BANK_ACCOUNT_IBAN = _('Parent bank account IBAN')
    LABEL_CHILD_NAME = _('Child name (without surnames)')
    LABEL_CHILD_SURNAMES = _('Child surnames')
    LABEL_CHILD_LEVEL = _('Child level (ex. HH4, LH3)')
    LABEL_CHILD_YEAR_OF_BIRTH = _('Child year of birth (ex. 2015)')
    LABEL_ASSISTED_DAYS = _('Assisted days in the selected edition')

    COLUMNS_TO_IMPORT = [
        [0, FieldsFormatters.clean_email, BaseImporter.KEY_FAMILY_EMAIL, LABEL_FAMILY_EMAIL],
        [1, FieldsFormatters.clean_name, BaseImporter.KEY_PARENT_NAME_AND_SURNAMES, LABEL_PARENT_NAME_AND_SURNAMES],
        [2, FieldsFormatters.clean_phone, BaseImporter.KEY_PARENT_PHONE_NUMBER, LABEL_PARENT_PHONE_NUMBER],
        [3, FieldsFormatters.clean_email, BaseImporter.KEY_PARENT_EMAIL, LABEL_PARENT_EMAIL],
        [4, FieldsFormattersDjango.clean_iban, BaseImporter.KEY_BANK_ACCOUNT_IBAN, LABEL_BANK_ACCOUNT_IBAN],
        [5, FieldsFormatters.clean_name, BaseImporter.KEY_CHILD_NAME, LABEL_CHILD_NAME],
        [6, FieldsFormatters.clean_name, BaseImporter.KEY_CHILD_SURNAMES, LABEL_CHILD_SURNAMES],
        [7, FieldsFormatters.clean_integer, BaseImporter.KEY_CHILD_YEAR_OF_BIRTH, LABEL_CHILD_YEAR_OF_BIRTH],
        [8, FieldsFormattersDjango.clean_level, BaseImporter.KEY_CHILD_LEVEL, LABEL_CHILD_LEVEL],
        [9, FieldsFormatters.clean_integer, BaseImporter.KEY_ASSISTED_DAYS, LABEL_ASSISTED_DAYS],
    ]

    def __init__(self, excel_content, custody_edition: CustodyEdition):
        self.excel_content = excel_content
        self.custody_edition = custody_edition
        self.rows = self.import_custody_new()

    def import_custody_new(self) -> list[Row]:
        manager = ExcelManager(self.excel_content, self.SHEET_NUMBER, self.FIRST_ROW_INDEX, self.COLUMNS_TO_IMPORT)

        for row in manager.rows:
            self.import_row(row)

        return manager.rows

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
            self.ensure_family_holders(family, holder)

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
