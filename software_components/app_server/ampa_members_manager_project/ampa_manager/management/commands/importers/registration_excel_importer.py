from ampa_manager.academic_course.models.level import Level
from ampa_manager.management.commands.importers.excel_importer import ExcelImporter
from ampa_manager.management.commands.results.processing_state import ProcessingState
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

    def import_row_fields(self, row_index: int):
        family_surnames = FieldsFormatters.clean_name(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_FAMILY_SURNAMES))
        child_name = FieldsFormatters.clean_name(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_CHILD_NAME))
        child_level = Level.parse_level(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_CHILD_LEVEL))
        child_year = FieldsFormatters.clean_integer(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_CHILD_YEAR))
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

        return RegistrationExcelRowFields(row_index, family_surnames, child_name, child_level, child_year,
                                       parent_name_and_surnames, parent_phone_number, parent_additional_phone_number,
                                       parent_email, bank_account_iban, after_school_name, edition_timetable,
                                       edition_period, edition_price_for_members, edition_price_for_no_members,
                                       edition_levels)


class RegistrationExcelRowFields:

    def __init__(self, row_index, family_surnames, child_name, child_level, child_year_of_birth, parent_name_and_surnames,
                 parent_phone_number, parent_additional_phone_number, parent_email, bank_account_iban,
                 after_school_name, edition_timetable, edition_period, edition_price_for_members,
                 edition_price_for_no_members, edition_levels):

        self.row_index = row_index
        self.family_surnames = family_surnames
        self.child_name = child_name
        self.child_level = child_level
        self.child_year_of_birth = child_year_of_birth
        self.parent_name_and_surnames = parent_name_and_surnames
        self.parent_phone_number = parent_phone_number
        self.parent_additional_phone_number = parent_additional_phone_number
        self.parent_email = parent_email
        self.bank_account_iban = bank_account_iban
        self.after_school_name = after_school_name
        self.edition_timetable = edition_timetable
        self.edition_period = edition_period
        self.edition_levels = edition_levels
        self.edition_price_for_members = edition_price_for_members
        self.edition_price_for_no_members = edition_price_for_no_members


class RegistrationImportResult:

    def __init__(self, row_index):
        self.row_index = row_index
        self.fields = RegistrationExcelRowFields(None, None, None, None, None, None, None, None, None, None, None, None,
                                                 None, None, None, None)
        self.family_state = ProcessingState.NOT_PROCESSED
        self.child_state = ProcessingState.NOT_PROCESSED
        self.parent_state = ProcessingState.NOT_PROCESSED
        self.bank_account_state = ProcessingState.NOT_PROCESSED
        self.after_school_state = ProcessingState.NOT_PROCESSED
        self.edition_state = ProcessingState.NOT_PROCESSED
        self.registration_state = ProcessingState.NOT_PROCESSED
        self.error = None
        self.registration = None

    @property
    def success(self):
        return self.registration is not None and self.error is None

    def print(self):
        summary = f'OK ({self.registration_state.name} #{self.registration.id})' if self.success else f'ERROR: {self.error}'

        print(f'\nRow {self.row_index + 1} -> {summary}')
        print(f' - Family: {self.fields.family_surnames} -> {self.family_state.name}')
        print(f' - Child: {self.fields.child_name}, {self.fields.child_level}, {self.fields.child_year_of_birth} -> {self.child_state.name}')
        print(f' - Parent: {self.fields.parent_name_and_surnames}, {self.fields.parent_phone_number}, {self.fields.parent_additional_phone_number}, {self.fields.parent_email} -> {self.parent_state.name}')
        print(f' - Bank account: {self.fields.bank_account_iban} -> {self.bank_account_state.name}')
        print(f' - After-school: {self.fields.after_school_name} -> {self.after_school_state.name}')
        print(f' - Edition: {self.fields.edition_timetable}, {self.fields.edition_period}, {self.fields.edition_levels}, {self.fields.edition_price_for_members}, {self.fields.edition_price_for_no_members} -> {self.edition_state.name}')

    @staticmethod
    def get_variation(before, after):
        if before < after:
            return f'{after} (+{after-before})'
        elif before > after:
            return f'{after} (-{before-after})'
        else:
            return f'{after} (=)'

    @staticmethod
    def print_stats(results, counts_before, counts_after):
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

        print('\nTOTAL')
        print(f'- IMPORTED: {imported_count}')
        print(f'- NOT IMPORTED: {not_imported_count}')

        print(f'\nFAMILIES {RegistrationImportResult.get_variation(counts_before["families"], counts_after["families"])}')
        for state, total in family_totals.items():
            print(f'- {state.name}: {total}')

        print(f'CHILDREN {RegistrationImportResult.get_variation(counts_before["children"], counts_after["children"])}')
        for state, total in child_totals.items():
            print(f'- {state.name}: {total}')

        print(f'PARENTS {RegistrationImportResult.get_variation(counts_before["parents"], counts_after["parents"])}')
        for state, total in parent_totals.items():
            print(f'- {state.name}: {total}')

        print(f'BANK ACCOUNTS {RegistrationImportResult.get_variation(counts_before["bank_accounts"], counts_after["bank_accounts"])}')
        for state, total in bank_account_totals.items():
            print(f'- {state.name}: {total}')

        print(f'AFTER SCHOOLS {RegistrationImportResult.get_variation(counts_before["after_schools"], counts_after["after_schools"])}')
        for state, total in after_school_totals.items():
            print(f'- {state.name}: {total}')

        print(f'EDITIONS {RegistrationImportResult.get_variation(counts_before["editions"], counts_after["editions"])}')
        for state, total in edition_totals.items():
            print(f'- {state.name}: {total}')

        print(f'REGISTRATIONS {RegistrationImportResult.get_variation(counts_before["registrations"], counts_after["registrations"])}')
        for state, total in registration_totals.items():
            print(f'- {state.name}: {total}')

        print(f'\nERRORS ({len(errors)}):')
        for error in errors:
            print(f'- {error}')

        if len(created_families) > 0:
            print(f'\nWARNING: {len(created_families)} families were created:')
            for family_surnames in created_families:
                print(f'- {family_surnames}')
