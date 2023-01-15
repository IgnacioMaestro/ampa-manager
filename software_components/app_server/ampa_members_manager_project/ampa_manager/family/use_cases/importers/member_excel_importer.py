from ampa_manager.academic_course.models.level import Level
from ampa_manager.family.use_cases.importers.member_excel_row import MemberExcelRow
from ampa_manager.management.commands.importers.excel_importer import ExcelImporter
from ampa_manager.utils.fields_formatters import FieldsFormatters
from ampa_manager.utils.string_utils import StringUtils


class MemberExcelImporter(ExcelImporter):
    COLUMN_INDEX_FAMILY_SURNAMES = 0

    COLUMN_INDEX_PARENT1_NAME_AND_SURNAMES = 1
    COLUMN_INDEX_PARENT1_PHONE = 2
    COLUMN_INDEX_PARENT1_ADDITIONAL_PHONE = 3
    COLUMN_INDEX_PARENT1_EMAIL = 4

    COLUMN_INDEX_PARENT1_BANK_ACCOUNT_SWIFT = 5
    COLUMN_INDEX_PARENT1_BANK_ACCOUNT_IBAN = 6
    COLUMN_INDEX_PARENT1_BANK_ACCOUNT_IS_DEFAULT = 7

    COLUMN_INDEX_PARENT2_NAME_AND_SURNAMES = 8
    COLUMN_INDEX_PARENT2_PHONE = 9
    COLUMN_INDEX_PARENT2_ADDITIONAL_PHONE = 10
    COLUMN_INDEX_PARENT2_EMAIL = 11

    COLUMN_INDEX_PARENT2_BANK_ACCOUNT_SWIFT = 12
    COLUMN_INDEX_PARENT2_BANK_ACCOUNT_IBAN = 13
    COLUMN_INDEX_PARENT2_BANK_ACCOUNT_IS_DEFAULT = 14

    COLUMN_INDEX_CHILD1_NAME = 15
    COLUMN_INDEX_CHILD1_LEVEL = 16
    COLUMN_INDEX_CHILD1_YEAR_OF_BIRTH = 17

    COLUMN_INDEX_CHILD2_NAME = 18
    COLUMN_INDEX_CHILD2_LEVEL = 19
    COLUMN_INDEX_CHILD2_YEAR_OF_BIRTH = 20

    COLUMN_INDEX_CHILD3_NAME = 21
    COLUMN_INDEX_CHILD3_LEVEL = 22
    COLUMN_INDEX_CHILD3_YEAR_OF_BIRTH = 23

    COLUMN_INDEX_CHILD4_NAME = 24
    COLUMN_INDEX_CHILD4_LEVEL = 25
    COLUMN_INDEX_CHILD4_YEAR_OF_BIRTH = 26

    COLUMN_INDEX_CHILD5_NAME = 27
    COLUMN_INDEX_CHILD5_LEVEL = 28
    COLUMN_INDEX_CHILD5_YEAR_OF_BIRTH = 29

    def import_row_columns(self, row_index: int):
        family_surnames = FieldsFormatters.clean_name(
            self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_FAMILY_SURNAMES))

        child1_name = FieldsFormatters.clean_name(
            self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_CHILD1_NAME))
        child1_level = Level.parse_level(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_CHILD1_LEVEL))
        child1_year_of_birth = FieldsFormatters.clean_integer(
            self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_CHILD1_YEAR_OF_BIRTH))

        child2_name = FieldsFormatters.clean_name(
            self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_CHILD2_NAME))
        child2_level = Level.parse_level(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_CHILD2_LEVEL))
        child2_year_of_birth = FieldsFormatters.clean_integer(
            self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_CHILD2_YEAR_OF_BIRTH))

        child3_name = FieldsFormatters.clean_name(
            self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_CHILD3_NAME))
        child3_level = Level.parse_level(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_CHILD3_LEVEL))
        child3_year_of_birth = FieldsFormatters.clean_integer(
            self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_CHILD3_YEAR_OF_BIRTH))

        child4_name = FieldsFormatters.clean_name(
            self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_CHILD4_NAME))
        child4_level = Level.parse_level(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_CHILD4_LEVEL))
        child4_year_of_birth = FieldsFormatters.clean_integer(
            self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_CHILD4_YEAR_OF_BIRTH))

        child5_name = FieldsFormatters.clean_name(
            self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_CHILD5_NAME))
        child5_level = Level.parse_level(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_CHILD5_LEVEL))
        child5_year_of_birth = FieldsFormatters.clean_integer(
            self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_CHILD5_YEAR_OF_BIRTH))

        parent1_name_and_surnames = FieldsFormatters.clean_name(
            self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_PARENT1_NAME_AND_SURNAMES))
        parent1_phone_number = FieldsFormatters.clean_phone(
            self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_PARENT1_PHONE))
        parent1_additional_phone_number = FieldsFormatters.clean_phone(
            self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_PARENT1_ADDITIONAL_PHONE))
        parent1_email = FieldsFormatters.clean_email(
            self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_PARENT1_EMAIL))

        parent2_name_and_surnames = FieldsFormatters.clean_name(
            self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_PARENT2_NAME_AND_SURNAMES))
        parent2_phone_number = FieldsFormatters.clean_phone(
            self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_PARENT2_PHONE))
        parent2_additional_phone_number = FieldsFormatters.clean_phone(
            self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_PARENT2_ADDITIONAL_PHONE))
        parent2_email = FieldsFormatters.clean_email(
            self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_PARENT2_EMAIL))

        parent1_bank_account_iban = FieldsFormatters.clean_iban(
            self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_PARENT1_BANK_ACCOUNT_IBAN))
        parent1_bank_account_swift_bic = FieldsFormatters.clean_string(
            self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_PARENT1_BANK_ACCOUNT_SWIFT))
        parent1_bank_account_is_default = StringUtils.parse_bool(
            self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_PARENT1_BANK_ACCOUNT_IS_DEFAULT))

        parent2_bank_account_iban = FieldsFormatters.clean_iban(
            self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_PARENT2_BANK_ACCOUNT_IBAN))
        parent2_bank_account_swift_bic = FieldsFormatters.clean_string(
            self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_PARENT2_BANK_ACCOUNT_SWIFT))
        parent2_bank_account_is_default = StringUtils.parse_bool(
            self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_PARENT2_BANK_ACCOUNT_IS_DEFAULT))

        return MemberExcelRow(row_index, family_surnames,
                              child1_name, child1_level, child1_year_of_birth,
                              child2_name, child2_level, child2_year_of_birth,
                              child3_name, child3_level, child3_year_of_birth,
                              child4_name, child4_level, child4_year_of_birth,
                              child5_name, child5_level, child5_year_of_birth,
                              parent1_name_and_surnames, parent1_phone_number, parent1_additional_phone_number, parent1_email,
                              parent2_name_and_surnames, parent2_phone_number, parent2_additional_phone_number, parent2_email,
                              parent1_bank_account_iban, parent1_bank_account_swift_bic, parent1_bank_account_is_default,
                              parent2_bank_account_iban, parent2_bank_account_swift_bic, parent2_bank_account_is_default)
