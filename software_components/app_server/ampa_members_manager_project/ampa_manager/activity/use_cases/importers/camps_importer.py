from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.after_school.after_school import AfterSchool
from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.activity.models.camps.camps_edition import CampsEdition
from ampa_manager.activity.models.camps.camps_registration import CampsRegistration
from ampa_manager.activity.use_cases.importers.camps_registration_importer import CampsRegistrationImporter
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
from ampa_manager.utils.fields_formatters import FieldsFormatters
from ampa_manager.utils.fields_formatters_django import FieldsFormattersDjango
from ampa_manager.views.import_info import ImportInfo


class CampsImporter:
    SHEET_NUMBER = 0
    FIRST_ROW_INDEX = 2

    KEY_FAMILY_EMAIL = 'family_email'
    KEY_PARENT_NAME_AND_SURNAMES = 'parent_name_and_surnames'
    KEY_PARENT_PHONE_NUMBER = 'parent_phone_number'
    KEY_PARENT_EMAIL = 'parent_email'
    KEY_BANK_ACCOUNT_IBAN = 'bank_account_iban'
    KEY_CHILD_NAME = 'child_name'
    KEY_CHILD_SURNAMES = 'child_surnames'
    KEY_CHILD_YEAR_OF_BIRTH = 'child_year_of_birth'
    KEY_CHILD_LEVEL = 'child_level'

    LABEL_FAMILY_EMAIL = _('Family email')
    LABEL_PARENT_NAME_AND_SURNAMES = _('Parent name and surnames')
    LABEL_PARENT_PHONE_NUMBER = _('Parent phone number')
    LABEL_PARENT_EMAIL = _('Parent email')
    LABEL_BANK_ACCOUNT_IBAN = _('Parent bank account IBAN')
    LABEL_CHILD_NAME = _('Child name (without surnames)')
    LABEL_CHILD_SURNAMES = _('Child surnames')
    LABEL_CHILD_YEAR_OF_BIRTH = _('Child year of birth (ex. 2015)')
    LABEL_CHILD_LEVEL = _('Child level (ex. HH4, LH3)')

    COLUMNS_TO_IMPORT = [
        [0, FieldsFormatters.clean_email, KEY_FAMILY_EMAIL, LABEL_FAMILY_EMAIL],
        [1, FieldsFormatters.clean_name, KEY_PARENT_NAME_AND_SURNAMES, LABEL_PARENT_NAME_AND_SURNAMES],
        [2, FieldsFormatters.clean_phone, KEY_PARENT_PHONE_NUMBER, LABEL_PARENT_PHONE_NUMBER],
        [3, FieldsFormatters.clean_email, KEY_PARENT_EMAIL, LABEL_PARENT_EMAIL],
        [4, FieldsFormattersDjango.clean_iban, KEY_BANK_ACCOUNT_IBAN, LABEL_BANK_ACCOUNT_IBAN],
        [5, FieldsFormatters.clean_name, KEY_CHILD_NAME, LABEL_CHILD_NAME],
        [6, FieldsFormatters.clean_name, KEY_CHILD_SURNAMES, LABEL_CHILD_SURNAMES],
        [7, FieldsFormatters.clean_integer, KEY_CHILD_YEAR_OF_BIRTH, LABEL_CHILD_YEAR_OF_BIRTH],
        [8, FieldsFormattersDjango.clean_level, KEY_CHILD_LEVEL, LABEL_CHILD_LEVEL],
    ]

    @classmethod
    def import_camps_registrations(cls, file_content, camps_edition: CampsEdition) -> ImportInfo:
        importer = ExcelImporter(
            cls.SHEET_NUMBER, cls.FIRST_ROW_INDEX, cls.COLUMNS_TO_IMPORT, file_content=file_content)

        importer.counters_before = cls.count_objects()

        for row in importer.get_rows():
            result = cls.process_row(row, camps_edition)
            importer.add_result(result)

        importer.counters_after = cls.count_objects()

        return ImportInfo(
            importer.total_rows, importer.successfully_imported_rows, importer.get_summary(), importer.get_results())

    @classmethod
    def count_objects(cls):
        return {
            Family.__name__: Family.objects.count(),
            Parent.__name__: Parent.objects.count(),
            Child.__name__: Child.objects.count(),
            BankAccount.__name__: BankAccount.objects.count(),
            Holder.__name__: Holder.objects.count(),
            CampsRegistration.__name__: AfterSchoolRegistration.objects.count()
        }

    @classmethod
    def process_row(cls, row: ExcelRow, camps_edition: CampsEdition) -> ImportRowResult:
        result = ImportRowResult(row)

        if row.error:
            result.error = row.error
            return result

        try:
            family_result = FamilyImporter.import_family(
                family_surnames=row.get(cls.KEY_CHILD_SURNAMES),
                parent1_name_and_surnames=row.get(cls.KEY_PARENT_NAME_AND_SURNAMES),
                child_name=row.get(cls.KEY_CHILD_NAME),
                email=row.get(cls.KEY_FAMILY_EMAIL))
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

            registration_result = CampsRegistrationImporter.import_registration(camps_edition, holder, child)
            result.add_partial_result(registration_result)

        except Exception as e:
            result.error = str(e)

        return result
