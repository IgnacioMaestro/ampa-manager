from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.activity.use_cases.importers.custody_registration_importer import CustodyRegistrationImporter
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.parent import Parent
from ampa_manager.family.use_cases.importers.bank_account_importer import BankAccountImporter
from ampa_manager.family.use_cases.importers.child_importer import ChildImporter
from ampa_manager.family.use_cases.importers.family_importer import FamilyImporter
from ampa_manager.family.use_cases.importers.parent_importer import ParentImporter
from ampa_manager.utils.excel.excel_importer import ExcelImporter
from ampa_manager.utils.excel.excel_row import ExcelRow
from ampa_manager.utils.excel.import_row_result import ImportRowResult
from ampa_manager.utils.excel.titled_list import TitledList
from ampa_manager.utils.fields_formatters import FieldsFormatters


class CustodyImporter:
    SHEET_NUMBER = 0
    FIRST_ROW_INDEX = 2

    KEY_PARENT_NAME_AND_SURNAMES = 'parent_name_and_surnames'
    KEY_PARENT_PHONE_NUMBER = 'parent_phone_number'
    KEY_PARENT_EMAIL = 'parent_email'
    KEY_BANK_ACCOUNT_IBAN = 'bank_account_iban'
    KEY_CHILD_NAME = 'child_name'
    KEY_CHILD_SURNAMES = 'child_surnames'
    KEY_CHILD_LEVEL = 'child_level'
    KEY_CHILD_YEAR_OF_BIRTH = 'child_year_of_birth'
    KEY_ASSISTED_DAYS = 'assisted_days'

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
        [0, FieldsFormatters.clean_name, KEY_PARENT_NAME_AND_SURNAMES, LABEL_PARENT_NAME_AND_SURNAMES],
        [1, FieldsFormatters.clean_phone, KEY_PARENT_PHONE_NUMBER, LABEL_PARENT_PHONE_NUMBER],
        [2, FieldsFormatters.clean_email, KEY_PARENT_EMAIL, LABEL_PARENT_EMAIL],
        [3, FieldsFormatters.clean_iban, KEY_BANK_ACCOUNT_IBAN, LABEL_BANK_ACCOUNT_IBAN],
        [4, FieldsFormatters.clean_name, KEY_CHILD_NAME, LABEL_CHILD_NAME],
        [5, FieldsFormatters.clean_name, KEY_CHILD_SURNAMES, LABEL_CHILD_SURNAMES],
        [6, FieldsFormatters.clean_integer, KEY_CHILD_YEAR_OF_BIRTH, LABEL_CHILD_YEAR_OF_BIRTH],
        [7, FieldsFormatters.clean_level, KEY_CHILD_LEVEL, LABEL_CHILD_LEVEL],
        [8, FieldsFormatters.clean_integer, KEY_ASSISTED_DAYS, LABEL_ASSISTED_DAYS],
    ]

    @classmethod
    def import_custody(cls, file_content, custody_edition: CustodyEdition) -> (int, int, TitledList, TitledList):
        importer = ExcelImporter(
            cls.SHEET_NUMBER, cls.FIRST_ROW_INDEX, cls.COLUMNS_TO_IMPORT, file_content=file_content)

        importer.counters_before = cls.count_objects()

        for row in importer.get_rows():
            result = cls.process_row(row, custody_edition)
            importer.add_result(result)

        importer.counters_after = cls.count_objects()

        return importer.total_rows, importer.successfully_imported_rows, importer.get_summary(), importer.get_results()

    @classmethod
    def count_objects(cls):
        return {
            Family.__name__: Family.objects.count(),
            Parent.__name__: Parent.objects.count(),
            Child.__name__: Child.objects.count(),
            BankAccount.__name__: BankAccount.objects.count(),
            Holder.__name__: Holder.objects.count(),
            CustodyRegistration.__name__: CustodyRegistration.objects.count(),
            CustodyEdition.__name__: CustodyEdition.objects.count(),
        }

    @classmethod
    def process_row(cls, row: ExcelRow, custody_edition: CustodyEdition) -> ImportRowResult:
        result = ImportRowResult(row)

        if row.error:
            result.error = row.error
            return result

        try:
            family_result = FamilyImporter.import_family(
                row.get(cls.KEY_CHILD_SURNAMES),
                row.get(cls.KEY_PARENT_NAME_AND_SURNAMES))
            result.add_partial_result(family_result)
            if not family_result.success:
                return result
            family = family_result.imported_object

            child_result = ChildImporter.import_child(
                family,
                row.get(cls.KEY_CHILD_NAME),
                row.get(cls.KEY_CHILD_LEVEL),
                row.get(cls.KEY_CHILD_YEAR_OF_BIRTH))
            result.add_partial_result(child_result)
            if not child_result.success:
                return result
            child = child_result.imported_object

            parent_result = ParentImporter.import_parent(
                family,
                row.get(cls.KEY_PARENT_NAME_AND_SURNAMES),
                row.get(cls.KEY_PARENT_PHONE_NUMBER),
                None,
                row.get(cls.KEY_PARENT_EMAIL))
            result.add_partial_result(parent_result)
            if not parent_result.success:
                return result
            parent = parent_result.imported_object

            bank_account_result, holder_result = BankAccountImporter.import_bank_account_and_holder(
                parent, row.get(
                    cls.KEY_BANK_ACCOUNT_IBAN))
            result.add_partial_result(bank_account_result)
            result.add_partial_result(holder_result)

            if not bank_account_result.success or not holder_result.success:
                return result
            holder = holder_result.imported_object

            registration_result = CustodyRegistrationImporter.import_registration(
                custody_edition, holder, child,
                row.get(cls.KEY_ASSISTED_DAYS))
            result.add_partial_result(registration_result)

        except Exception as e:
            result.error = str(e)

        return result
