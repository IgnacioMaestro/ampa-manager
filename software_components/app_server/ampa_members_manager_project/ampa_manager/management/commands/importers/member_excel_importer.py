from dataclasses import dataclass
from typing import Optional

from ampa_manager.academic_course.models.level import Level
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.parent import Parent
from ampa_manager.management.commands.importers.excel_importer import ExcelImporter
from ampa_manager.management.commands.results.processing_state import ProcessingState
from ampa_manager.management.commands.utils.logger import Logger
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

        return MemberExcelRowFields(row_index, family_surnames,
                                    child1_name, child1_level, child1_year_of_birth,
                                    child2_name, child2_level, child2_year_of_birth,
                                    child3_name, child3_level, child3_year_of_birth,
                                    child4_name, child4_level, child4_year_of_birth,
                                    child5_name, child5_level, child5_year_of_birth,
                                    parent1_name_and_surnames, parent1_phone_number, parent1_additional_phone_number, parent1_email,
                                    parent2_name_and_surnames, parent2_phone_number, parent2_additional_phone_number, parent2_email,
                                    parent1_bank_account_iban, parent1_bank_account_swift_bic, parent1_bank_account_is_default,
                                    parent2_bank_account_iban, parent2_bank_account_swift_bic, parent2_bank_account_is_default)


@dataclass
class MemberExcelRowFields:

    row_index: Optional[int]
    family_surnames: Optional[str]
    child1_name: Optional[str]
    child1_level: Optional[str]
    child1_year_of_birth: Optional[int]
    child2_name: Optional[str]
    child2_level: Optional[str]
    child2_year_of_birth: Optional[int]
    child3_name: Optional[str]
    child3_level: Optional[str]
    child3_year_of_birth: Optional[int]
    child4_name: Optional[str]
    child4_level: Optional[str]
    child4_year_of_birth: Optional[int]
    child5_name: Optional[str]
    child5_level: Optional[str]
    child5_year_of_birth: Optional[int]
    parent1_name_and_surnames: Optional[str]
    parent1_phone_number: Optional[str]
    parent1_additional_phone_number: Optional[str]
    parent1_email: Optional[str]
    parent2_name_and_surnames: Optional[str]
    parent2_phone_number: Optional[str]
    parent2_additional_phone_number: Optional[str]
    parent2_email: Optional[str]
    parent1_bank_account_iban: Optional[str]
    parent1_bank_account_swift_bic: Optional[str]
    parent1_bank_account_is_default: Optional[bool]
    parent2_bank_account_iban: Optional[str]
    parent2_bank_account_swift_bic: Optional[str]
    parent2_bank_account_is_default: Optional[bool]

    def child1_has_data(self):
        return self.child1_name or self.child1_level or self.child1_year_of_birth

    def child2_has_data(self):
        return self.child2_name or self.child2_level or self.child2_year_of_birth

    def child3_has_data(self):
        return self.child3_name or self.child3_level or self.child3_year_of_birth

    def child4_has_data(self):
        return self.child4_name or self.child4_level or self.child4_year_of_birth

    def child5_has_data(self):
        return self.child5_name or self.child5_level or self.child5_year_of_birth

    def parent1_has_data(self):
        return self.parent1_name_and_surnames or self.parent1_phone_number or self.parent1_additional_phone_number or self.parent1_email

    def parent2_has_data(self):
        return self.parent2_name_and_surnames or self.parent2_phone_number or self.parent2_additional_phone_number or self.parent2_email

    def parent1_bank_account_has_data(self):
        return self.parent1_bank_account_iban or self.parent1_bank_account_swift_bic or self.parent1_bank_account_is_default

    def parent2_bank_account_has_data(self):
        return self.parent2_bank_account_iban or self.parent2_bank_account_swift_bic or self.parent2_bank_account_is_default

class MemberImportResult:

    def __init__(self, row_index):
        self.row_index = row_index
        self.fields = MemberExcelRowFields(None, None, None, None, None, None, None, None, None, None, None, None,
                                           None, None, None, None, None, None, None, None, None, None, None, None,
                                           None, None, None, None, None, None, None)
        self.family_state = ProcessingState.NOT_PROCESSED
        self.child1_state = ProcessingState.NOT_PROCESSED
        self.child2_state = ProcessingState.NOT_PROCESSED
        self.child3_state = ProcessingState.NOT_PROCESSED
        self.child4_state = ProcessingState.NOT_PROCESSED
        self.child5_state = ProcessingState.NOT_PROCESSED
        self.parent1_state = ProcessingState.NOT_PROCESSED
        self.parent2_state = ProcessingState.NOT_PROCESSED
        self.parent1_bank_account_state = ProcessingState.NOT_PROCESSED
        self.parent2_bank_account_state = ProcessingState.NOT_PROCESSED
        self.errors = []

    @property
    def success(self):
        return len(self.errors) == 0

    def print(self, logger: Logger):
        logger.log(f'\nRow {self.row_index + 1}')
        logger.log(f' - Family: {self.fields.family_surnames} -> {self.family_state.name}')
        logger.log(f' - Parent 1: {self.fields.parent1_name_and_surnames}, {self.fields.parent1_phone_number}, {self.fields.parent1_additional_phone_number}, {self.fields.parent1_email} -> {self.parent1_state.name}')
        logger.log(f' - Parent 2: {self.fields.parent2_name_and_surnames}, {self.fields.parent2_phone_number}, {self.fields.parent2_additional_phone_number}, {self.fields.parent2_email} -> {self.parent2_state.name}')
        logger.log(f' - Child 1: {self.fields.child1_name}, {self.fields.child1_level}, {self.fields.child1_year_of_birth} -> {self.child1_state.name}')
        logger.log(f' - Child 2: {self.fields.child2_name}, {self.fields.child2_level}, {self.fields.child2_year_of_birth} -> {self.child2_state.name}')
        logger.log(f' - Child 3: {self.fields.child3_name}, {self.fields.child3_level}, {self.fields.child3_year_of_birth} -> {self.child3_state.name}')
        logger.log(f' - Child 4: {self.fields.child4_name}, {self.fields.child4_level}, {self.fields.child4_year_of_birth} -> {self.child4_state.name}')
        logger.log(f' - Child 5: {self.fields.child5_name}, {self.fields.child5_level}, {self.fields.child5_year_of_birth} -> {self.child5_state.name}')
        logger.log(f' - Parent 1 Bank account: {self.fields.parent1_bank_account_iban}, {self.fields.parent1_bank_account_swift_bic}, {self.fields.parent1_bank_account_is_default} -> {self.parent1_bank_account_state.name}')
        logger.log(f' - Parent 2 Bank account: {self.fields.parent1_bank_account_iban}, {self.fields.parent1_bank_account_swift_bic}, {self.fields.parent1_bank_account_is_default} -> {self.parent1_bank_account_state.name}')

    @staticmethod
    def get_variation(before, after):
        if before < after:
            return f'{after} (+{after-before})'
        elif before > after:
            return f'{after} (-{before-after})'
        else:
            return f'{after} (=)'

    @staticmethod
    def print_stats(logger, results, counts_before, counts_after):
        imported_count = 0
        not_imported_count = 0

        family_totals = {}
        child_totals = {}
        parent_totals = {}
        bank_account_totals = {}
        after_school_totals = {}
        edition_totals = {}
        registration_totals = {}

        errors = []
        created_families = []

        for result in results:
            if result.success:
                imported_count += 1
            else:
                not_imported_count += 1
                errors.append(f'Row {result.row_index + 1}: {result.error}')

            if result.family_state == ProcessingState.CREATED:
                created_families.append(result.fields.family_surnames)

            if result.family_state not in family_totals:
                family_totals[result.family_state] = 1
            else:
                family_totals[result.family_state] += 1

            if result.child_state not in child_totals:
                child_totals[result.child_state] = 1
            else:
                child_totals[result.child_state] += 1

            if result.parent_state not in parent_totals:
                parent_totals[result.parent_state] = 1
            else:
                parent_totals[result.parent_state] += 1

            if result.bank_account_state not in bank_account_totals:
                bank_account_totals[result.bank_account_state] = 1
            else:
                bank_account_totals[result.bank_account_state] += 1

            if result.after_school_state not in after_school_totals:
                after_school_totals[result.after_school_state] = 1
            else:
                after_school_totals[result.after_school_state] += 1

            if result.edition_state not in edition_totals:
                edition_totals[result.edition_state] = 1
            else:
                edition_totals[result.edition_state] += 1

            if result.registration_state not in registration_totals:
                registration_totals[result.registration_state] = 1
            else:
                registration_totals[result.registration_state] += 1

        logger.log('\nTOTAL')
        logger.log(f'- IMPORTED: {imported_count}')
        logger.log(f'- NOT IMPORTED: {not_imported_count}')

        logger.log(f'\nFAMILIES {RegistrationImportResult.get_variation(counts_before["families"], counts_after["families"])}')
        for state, total in family_totals.items():
            logger.log(f'- {state.name}: {total}')

        logger.log(f'CHILDREN {RegistrationImportResult.get_variation(counts_before["children"], counts_after["children"])}')
        for state, total in child_totals.items():
            logger.log(f'- {state.name}: {total}')

        logger.log(f'PARENTS {RegistrationImportResult.get_variation(counts_before["parents"], counts_after["parents"])}')
        for state, total in parent_totals.items():
            logger.log(f'- {state.name}: {total}')

        logger.log(f'BANK ACCOUNTS {RegistrationImportResult.get_variation(counts_before["bank_accounts"], counts_after["bank_accounts"])}')
        for state, total in bank_account_totals.items():
            logger.log(f'- {state.name}: {total}')

        logger.log(f'AFTER SCHOOLS {RegistrationImportResult.get_variation(counts_before["after_schools"], counts_after["after_schools"])}')
        for state, total in after_school_totals.items():
            logger.log(f'- {state.name}: {total}')

        logger.log(f'EDITIONS {RegistrationImportResult.get_variation(counts_before["editions"], counts_after["editions"])}')
        for state, total in edition_totals.items():
            logger.log(f'- {state.name}: {total}')

        logger.log(f'REGISTRATIONS {RegistrationImportResult.get_variation(counts_before["registrations"], counts_after["registrations"])}')
        for state, total in registration_totals.items():
            logger.log(f'- {state.name}: {total}')

        logger.log(f'\nERRORS ({len(errors)}):')
        for error in errors:
            logger.log(f'- {error}')

        if len(created_families) > 0:
            logger.log(f'\nWARNING: {len(created_families)} families were created:')
            for family_surnames in created_families:
                logger.log(f'- {family_surnames}')

    def print_stats(self):
        self.logger.log('\nSUMMARY\n')

        rows_with_data_count = self.sheet.nrows - Command.FIRST_ROW_INDEX
        self.logger.log(
            f' - Rows with data: {rows_with_data_count} (rows {Command.FIRST_ROW_INDEX + 1} to {self.sheet.nrows}). Sheet: "{self.sheet.name}"')

        self.totals = self.totalize_results()
        for class_name, states in self.totals.items():
            variation = self.get_totals_variation(class_name)
            self.logger.log(f' - {class_name} ({variation}):')

            for state, total in states.items():
                self.logger.log(f'   - {state.name}: {total}:')

        self.logger.log(f'\nVALIDATIONS:\n')

        warnings = Parent.review_data()
        for warning in warnings:
            self.logger.log(warning)

        warnings = Family.review_data()
        for warning in warnings:
            self.logger.log(warning)

        errors = self.get_errors()
        self.logger.log(f'\nERRORS ({len(errors)}):\n')
        if len(errors) > 0:
            for error in errors:
                self.logger.error(f'- {error} ')
        else:
            self.logger.log(f'- No errors\n')

    def add_error(self, error):
        if error:
            self.errors.append(error)
