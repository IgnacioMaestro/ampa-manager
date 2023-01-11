from ampa_manager.academic_course.models.level import Level
from ampa_manager.activity.use_cases.importers.registration_excel_row import RegistrationExcelRow
from ampa_manager.management.commands.importers.excel_importer import ExcelImporter
from ampa_manager.utils.fields_formatters import FieldsFormatters


class RegistrationExcelImporter(ExcelImporter):
    COLUMN_INDEX_FAMILY_SURNAMES = 0
    COLUMN_INDEX_CHILD_NAME = 1
    COLUMN_INDEX_CHILD_LEVEL = 3
    COLUMN_INDEX_CHILD_YEAR = 4
    COLUMN_INDEX_PARENT_PHONE = 5
    COLUMN_INDEX_PARENT_ADDITIONAL_PHONE = 6
    COLUMN_INDEX_PARENT_EMAIL = 7
    COLUMN_INDEX_PARENT_NAME_AND_SURNAMES = 8
    COLUMN_INDEX_BANK_ACCOUNT_IBAN = 10
    COLUMN_INDEX_AFTER_SCHOOL_NAME = 11
    COLUMN_INDEX_EDITION_PERIOD = 12
    COLUMN_INDEX_EDITION_TIMETABLE = 13
    COLUMN_INDEX_EDITION_LEVELS = 14
    COLUMN_INDEX_EDITION_PRICE_FOR_MEMBERS = 15
    COLUMN_INDEX_EDITION_PRICE_FOR_NO_MEMBERS = 16

    def import_row_columns(self, row_index: int) -> RegistrationExcelRow:
        family_surnames = FieldsFormatters.clean_name(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_FAMILY_SURNAMES))
        child_name = FieldsFormatters.clean_name(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_CHILD_NAME))
        child_level = Level.parse_level(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_CHILD_LEVEL))
        child_year_of_birth = FieldsFormatters.clean_integer(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_CHILD_YEAR))
        parent_name_and_surnames = FieldsFormatters.clean_name(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_PARENT_NAME_AND_SURNAMES))
        parent_phone_number = FieldsFormatters.clean_phone(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_PARENT_PHONE))
        parent_additional_phone_number = FieldsFormatters.clean_phone(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_PARENT_ADDITIONAL_PHONE))
        parent_email = FieldsFormatters.clean_email(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_PARENT_EMAIL))
        bank_account_iban = FieldsFormatters.clean_iban(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_BANK_ACCOUNT_IBAN))
        after_school_name = FieldsFormatters.clean_string(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_AFTER_SCHOOL_NAME))
        edition_timetable = FieldsFormatters.clean_string(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_EDITION_TIMETABLE))
        edition_period = FieldsFormatters.clean_string(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_EDITION_PERIOD))
        edition_levels = FieldsFormatters.clean_string(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_EDITION_LEVELS))
        edition_price_for_members = FieldsFormatters.clean_integer(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_EDITION_PRICE_FOR_MEMBERS))
        edition_price_for_no_members = FieldsFormatters.clean_integer(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_EDITION_PRICE_FOR_NO_MEMBERS))

        return RegistrationExcelRow(row_index, family_surnames, child_name, child_level, child_year_of_birth,
                                    parent_name_and_surnames, parent_phone_number, parent_additional_phone_number,
                                    parent_email, bank_account_iban, after_school_name, edition_timetable,
                                    edition_period, edition_levels, edition_price_for_members,
                                    edition_price_for_no_members)
