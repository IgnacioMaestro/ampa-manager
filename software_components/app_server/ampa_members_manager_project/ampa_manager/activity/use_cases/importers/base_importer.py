from typing import Optional

from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.activity.models.camps.camps_registration import CampsRegistration
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.activity.use_cases.importers.excel_column_definition import ExcelColumnDefinition
from ampa_manager.activity.use_cases.importers.excel_data_extractor_pandas import ExcelDataExtractorPandas
from ampa_manager.activity.use_cases.importers.import_excel_result import ImportExcelResult
from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult
from ampa_manager.activity.use_cases.importers.row import Row
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.parent import Parent
from ampa_manager.family.use_cases.importers.bank_account_importer import BankAccountImporter
from ampa_manager.family.use_cases.importers.child_importer import ChildImporter
from ampa_manager.family.use_cases.importers.family_importer import FamilyImporter
from ampa_manager.family.use_cases.importers.holder_importer import HolderImporter
from ampa_manager.family.use_cases.importers.parent_importer import ParentImporter
from ampa_manager.utils.fields_formatters import FieldsFormatters
from ampa_manager.utils.string_utils import StringUtils


class BaseImporter:
    SHEET_NUMBER = 0
    FIRST_ROW_INDEX = 2
    COLUMNS_TO_IMPORT = []

    KEY_FAMILY_EMAIL = 'family_email'
    KEY_FAMILY_SURNAMES = 'family_surnames'
    KEY_PARENT_1_NAME_AND_SURNAMES = 'parent_1_name_and_surnames'
    KEY_PARENT_1_PHONE_NUMBER = 'parent_1_phone_number'
    KEY_PARENT_1_EMAIL = 'parent_1_email'
    KEY_PARENT_2_NAME_AND_SURNAMES = 'parent_2_name_and_surnames'
    KEY_PARENT_2_PHONE_NUMBER = 'parent_2_phone_number'
    KEY_PARENT_2_EMAIL = 'parent_2_email'
    KEY_BANK_ACCOUNT_IBAN = 'bank_account_iban'
    KEY_CHILD_1_NAME = 'child_1_name'
    KEY_CHILD_1_LEVEL = 'child_1_level'
    KEY_CHILD_1_YEAR_OF_BIRTH = 'child_1_year_of_birth'
    KEY_CHILD_2_NAME = 'child_2_name'
    KEY_CHILD_2_LEVEL = 'child_2_level'
    KEY_CHILD_2_YEAR_OF_BIRTH = 'child_2_year_of_birth'
    KEY_CHILD_3_NAME = 'child_3_name'
    KEY_CHILD_3_LEVEL = 'child_3_level'
    KEY_CHILD_3_YEAR_OF_BIRTH = 'child_3_year_of_birth'
    KEY_CHILD_4_NAME = 'child_4_name'
    KEY_CHILD_4_LEVEL = 'child_4_level'
    KEY_CHILD_4_YEAR_OF_BIRTH = 'child_4_year_of_birth'
    KEY_ASSISTED_DAYS = 'assisted_days'

    family_email = ExcelColumnDefinition(
        KEY_FAMILY_EMAIL, _('Family email'), _('Family email'), FieldsFormatters.format_email)
    family_surnames = ExcelColumnDefinition(
        KEY_FAMILY_SURNAMES, _('Family surnames'), _('Family surnames'), FieldsFormatters.format_name)
    parent_1_name_and_surnames = ExcelColumnDefinition(
        KEY_PARENT_1_NAME_AND_SURNAMES, _('Parent 1 name and surnames'), _('Parent name and surnames'),
        FieldsFormatters.format_name)
    parent_1_phone_number = ExcelColumnDefinition(
        KEY_PARENT_1_PHONE_NUMBER, _('Parent 1 phone number'), _('Parent phone number'), FieldsFormatters.format_phone)
    parent_1_email = ExcelColumnDefinition(
        KEY_PARENT_1_EMAIL, _('Parent 1 email'), _('Parent email'), FieldsFormatters.format_email)
    parent_2_name_and_surnames = ExcelColumnDefinition(
        KEY_PARENT_2_NAME_AND_SURNAMES, _('Parent 2 name and surnames'), _('Parent 2 name and surnames'),
        FieldsFormatters.format_name)
    parent_2_phone_number = ExcelColumnDefinition(
        KEY_PARENT_2_PHONE_NUMBER, _('Parent 2 phone number'), _('Parent 2 phone number'), FieldsFormatters.format_phone)
    parent_2_email = ExcelColumnDefinition(
        KEY_PARENT_2_EMAIL, _('Parent 2 email'), _('Parent 2 email'), FieldsFormatters.format_email)
    bank_account_iban = ExcelColumnDefinition(
        KEY_BANK_ACCOUNT_IBAN, _('Bank account IBAN'), _('Bank account IBAN'), FieldsFormatters.format_iban)
    child_1_name = ExcelColumnDefinition(
        KEY_CHILD_1_NAME, _('Child 1 name'), _('Child name'), FieldsFormatters.format_name)
    child_1_level = ExcelColumnDefinition(
        KEY_CHILD_1_LEVEL, _('Child 1 level'), _('Child level'), FieldsFormatters.format_level)
    child_1_year_of_birth = ExcelColumnDefinition(
        KEY_CHILD_1_YEAR_OF_BIRTH, _('Child 1 year of birth'), _('Child year of birth'),
        FieldsFormatters.format_integer)
    child_2_name = ExcelColumnDefinition(
        KEY_CHILD_2_NAME, _('Child 2 name'), _('Child 2 name'), FieldsFormatters.format_name)
    child_2_level = ExcelColumnDefinition(
        KEY_CHILD_2_LEVEL, _('Child 2 level'), _('Child 2 level'), FieldsFormatters.format_level)
    child_2_year_of_birth = ExcelColumnDefinition(
        KEY_CHILD_2_YEAR_OF_BIRTH, _('Child 2 year of birth'), _('Child 2 year of birth'),
        FieldsFormatters.format_integer)
    child_3_name = ExcelColumnDefinition(
        KEY_CHILD_3_NAME, _('Child 3 name'), _('Child 3 name'), FieldsFormatters.format_name)
    child_3_level = ExcelColumnDefinition(
        KEY_CHILD_3_LEVEL, _('Child 3 level'), _('Child 3 level'), FieldsFormatters.format_level)
    child_3_year_of_birth = ExcelColumnDefinition(
        KEY_CHILD_3_YEAR_OF_BIRTH, _('Child 3 year of birth'), _('Child 3 year of birth'),
        FieldsFormatters.format_integer)
    child_4_name = ExcelColumnDefinition(
        KEY_CHILD_4_NAME, _('Child 4 name'), _('Child 4 name'), FieldsFormatters.format_name)
    child_4_level = ExcelColumnDefinition(
        KEY_CHILD_4_LEVEL, _('Child 4 level'), _('Child 4 level'), FieldsFormatters.format_level)
    child_4_year_of_birth = ExcelColumnDefinition(
        KEY_CHILD_4_YEAR_OF_BIRTH, _('Child 4 year of birth'), _('Child 4 year of birth'),
        FieldsFormatters.format_integer)
    assisted_days = ExcelColumnDefinition(
        'assisted_days', _('Assisted days in the selected edition'), _('Assistance'),
        FieldsFormatters.format_integer)

    def __init__(self, excel_content: bytes):
        self.excel_content: bytes = excel_content

    def run(self) -> ImportExcelResult:
        rows: list[Row] = ExcelDataExtractorPandas(
            self.excel_content, self.SHEET_NUMBER, self.FIRST_ROW_INDEX, self.COLUMNS_TO_IMPORT).extract()

        for row in rows:
            self.process_row(row)

        return ImportExcelResult(rows)

    def process_row(self, row: Row):
        raise NotImplementedError

    @classmethod
    def import_family(cls, row: Row) -> Optional[Family]:
        family_surnames = row.get_value(cls.KEY_FAMILY_SURNAMES)
        family_email = row.get_value(cls.KEY_FAMILY_EMAIL)

        result: ImportModelResult = FamilyImporter(
            family_surnames=family_surnames,
            family_email=family_email).import_family()
        row.add_imported_model_result(result)

        return result.instance

    @classmethod
    def import_child(cls, row: Row, family: Family) -> Optional[Child]:
        name = row.get_value(cls.KEY_CHILD_1_NAME)
        level = row.get_value(cls.KEY_CHILD_1_LEVEL)
        year_of_birth = row.get_value(cls.KEY_CHILD_1_YEAR_OF_BIRTH)

        result: ImportModelResult = ChildImporter(
            family=family,
            name=name,
            level=level,
            year_of_birth=year_of_birth).import_child()

        row.add_imported_model_result(result)

        return result.instance

    @classmethod
    def import_parent(cls, row: Row, family: Family, compulsory: bool) -> Optional[Parent]:
        name_and_surnames = row.get_value(cls.KEY_PARENT_1_NAME_AND_SURNAMES)
        phone_number = row.get_value(cls.KEY_PARENT_1_PHONE_NUMBER)
        email = row.get_value(cls.KEY_PARENT_1_EMAIL)

        result: ImportModelResult = ParentImporter(
            family=family,
            name_and_surnames=name_and_surnames,
            phone_number=phone_number,
            additional_phone_number=None,
            email=email,
            compulsory=compulsory).import_parent()

        row.add_imported_model_result(result)

        return result.instance

    @classmethod
    def import_bank_account_and_holder(cls, row: Row, parent: Parent) -> Optional[Holder]:
        iban = row.get_value(cls.KEY_BANK_ACCOUNT_IBAN)

        account_result: ImportModelResult = BankAccountImporter(
            parent=parent,
            iban=iban).import_bank_account()
        row.add_imported_model_result(account_result)

        if not account_result.instance:
            return None

        holder_result: ImportModelResult = HolderImporter(
            parent=parent,
            bank_account=account_result.instance).import_holder()
        row.add_imported_model_result(holder_result)

        return holder_result.instance
