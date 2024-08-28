from typing import Optional

import xlrd
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.activity.models.camps.camps_registration import CampsRegistration
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.parent import Parent
from ampa_manager.family.use_cases.importers.bank_account_importer import BankAccountImporter
from ampa_manager.family.use_cases.importers.child_importer import ChildImporter
from ampa_manager.family.use_cases.importers.family_importer import FamilyImporter
from ampa_manager.family.use_cases.importers.parent_importer import ParentImporter
from ampa_manager.utils.excel.import_model_result import ImportModelResult


class Column:
    def __init__(self, raw_value, formatted_value, error=None):
        self.value: str = raw_value
        self.formatted_value = formatted_value
        self.error: Optional[str] = error


class Row:
    def __init__(self, row_index: int):
        self.row_index: int = row_index
        self.values: dict[str, Column] = {}
        self.imported_models: list[ImportModelResult] = []
        self.error: Optional[str] = None

    def set_error(self, error: str):
        self.error = error

    def add_value(self, key: str, value: Column):
        self.values[key] = value

    def add_imported_model(self, imported_model: ImportModelResult):
        self.imported_models.append(imported_model)

    def get_value(self, key: str):
        return self.values[key].formatted_value

    @property
    def any_error(self) -> bool:
        if self.error:
            return True
        for value in self.values.values():
            if value.error:
                return True
        return False


class ExcelManager:
    def __init__(self, excel_content, sheet_number: int, first_row_index: int, columns_to_extract: list):
        self.excel_content = excel_content
        self.sheet_number = sheet_number
        self.first_row_index = first_row_index
        self.columns_to_extract = columns_to_extract
        self.book = xlrd.open_workbook(file_contents=self.excel_content)
        self.sheet = self.book.sheet_by_index(self.sheet_number)
        self.rows = self.extract_excel_data()

        if self.first_row_index > self.sheet.nrows:
            raise Exception('Invalid first row index')

    def extract_excel_data(self) -> list[Row]:
        rows = []
        for row_index in range(self.first_row_index, self.sheet.nrows):
            row = Row(row_index)

            for column_settings in self.columns_to_extract:
                col_index = column_settings[0]
                formatter = column_settings[1]
                key = column_settings[2]
                row.add_value(key, self.get_column(row_index, col_index, formatter))

            rows.append(row)
        return rows

    def get_column(self, row_index: int, col_index: int, formatter) -> Column:
        raw_value = None
        formatted_value = None
        error = None

        try:
            raw_value = self.sheet.cell_value(rowx=row_index, colx=col_index)
            formatted_value = formatter(raw_value)
        except Exception as e:
            error = str(e)

        return Column(raw_value, formatted_value, error)


class ImportSummary:

    def __init__(self, rows: list[Row]):
        self.rows: list[Row] = rows


class BaseImporter:
    KEY_FAMILY_EMAIL = 'family_email'
    KEY_PARENT_NAME_AND_SURNAMES = 'parent_name_and_surnames'
    KEY_PARENT_PHONE_NUMBER = 'parent_phone_number'
    KEY_PARENT_EMAIL = 'parent_email'
    KEY_BANK_ACCOUNT_IBAN = 'bank_account_iban'
    KEY_CHILD_NAME = 'child_name'
    KEY_CHILD_SURNAMES = 'child_surnames'
    KEY_CHILD_LEVEL = 'child_level'
    KEY_CHILD_YEAR_OF_BIRTH = 'child_year_of_birth'
    KEY_ASSISTED_DAYS = 'assisted_days'

    LABEL_FAMILY_EMAIL = _('Family email')
    LABEL_PARENT_NAME_AND_SURNAMES = _('Parent name and surnames')
    LABEL_PARENT_PHONE_NUMBER = _('Parent phone number')
    LABEL_PARENT_EMAIL = _('Parent email')
    LABEL_BANK_ACCOUNT_IBAN = _('Parent bank account IBAN')
    LABEL_CHILD_NAME = _('Child name (without surnames)')
    LABEL_CHILD_SURNAMES = _('Child surnames')
    LABEL_CHILD_LEVEL = _('Child level (ex. HH4, LH3)')
    LABEL_CHILD_YEAR_OF_BIRTH = _('Child year of birth (ex. 2015)')

    @classmethod
    def import_family(cls, row: Row) -> Family:
        family_surnames = row.get_value(cls.KEY_CHILD_SURNAMES)
        parent1_name_and_surnames = row.get_value(cls.KEY_PARENT_NAME_AND_SURNAMES)
        child_name = row.get_value(cls.KEY_CHILD_NAME)
        email = row.get_value(cls.KEY_FAMILY_EMAIL)

        imported_model: ImportModelResult = FamilyImporter.import_family(
            family_surnames=family_surnames,
            parent1_name_and_surnames=parent1_name_and_surnames,
            child_name=child_name,
            email=email)
        row.add_imported_model(imported_model)

        return imported_model.imported_object

    @classmethod
    def import_child(cls, row: Row, family: Family) -> Child:
        name = row.get_value(cls.KEY_CHILD_NAME)
        level = row.get_value(cls.KEY_CHILD_LEVEL)
        year_of_birth = row.get_value(cls.KEY_CHILD_YEAR_OF_BIRTH)

        imported_model: ImportModelResult = ChildImporter.import_child(
            family=family,
            name=name,
            level=level,
            year_of_birth=year_of_birth)

        row.add_imported_model(imported_model)

        return imported_model.imported_object

    @classmethod
    def import_parent(cls, row: Row, family: Family) -> Parent:
        name_and_surnames = row.get_value(cls.KEY_PARENT_NAME_AND_SURNAMES)
        phone_number = row.get_value(cls.KEY_PARENT_PHONE_NUMBER)
        email = row.get_value(cls.KEY_PARENT_EMAIL)

        imported_model: ImportModelResult = ParentImporter.import_parent(
            family=family,
            name_and_surnames=name_and_surnames,
            phone_number=phone_number,
            additional_phone_number=None,
            email=email,
            optional=True)

        row.add_imported_model(imported_model)

        return imported_model.imported_object

    @classmethod
    def import_bank_account_and_holder(cls, row: Row, parent: Parent) -> Holder:
        iban = row.get_value(cls.KEY_BANK_ACCOUNT_IBAN)

        bank_account_result, holder_result = BankAccountImporter.import_bank_account_and_holder(
            parent=parent,
            iban=iban)
        row.add_imported_model(bank_account_result)
        row.add_imported_model(holder_result)

        return holder_result.imported_object

    @classmethod
    def consolidate_family_holders(cls, family: Family):
        if not family.custody_holder:
            family.custody_holder = cls.get_last_custody_registration_holder(family)
        if not family.after_school_holder:
            family.after_school_holder = cls.get_last_after_school_registration_holder(family)
        if not family.camps_holder:
            family.camps_holder = cls.get_last_camps_registration_holder(family)

        if not family.membership_holder:
            family.membership_holder = family.get_default_holder()

        if not family.custody_holder:
            family.custody_holder = family.membership_holder
        if not family.after_school_holder:
            family.after_school_holder = family.membership_holder
        if not family.camps_holder:
            family.camps_holder = family.membership_holder

    @classmethod
    def get_last_custody_registration_holder(cls, family: Family):
        registrations = CustodyRegistration.objects.of_family(family).order_by('-id')
        if registrations.exists():
            return registrations.last().holder
        return None

    @classmethod
    def get_last_after_school_registration_holder(cls, family: Family):
        registrations = AfterSchoolRegistration.objects.of_family(family).order_by('-id')
        if registrations.exists():
            return registrations.last().holder
        return None

    @classmethod
    def get_last_camps_registration_holder(cls, family: Family):
        registrations = CampsRegistration.objects.of_family(family).order_by('-id')
        if registrations.exists():
            return registrations.last().holder
        return None
