from ampa_manager.family.models.family import Family
from ampa_manager.family.models.parent import Parent
from ampa_manager.family.use_cases.importers.member_excel_row import MemberExcelRow
from ampa_manager.management.commands.importers.registration_import_result import RegistrationImportResult
from ampa_manager.management.commands.results.processing_state import ProcessingState
from ampa_manager.management.commands.utils.logger import Logger


class MemberImportResult:

    def __init__(self, row_index):
        self.row_index = row_index
        self.fields = MemberExcelRow(None, None, None, None, None, None, None, None, None, None, None, None,
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
        logger.log(f'Row {self.row_index + 1}')
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

        logger.log('TOTAL')
        logger.log(f'- IMPORTED: {imported_count}')
        logger.log(f'- NOT IMPORTED: {not_imported_count}')

        logger.log(f'FAMILIES {RegistrationImportResult.get_variation(counts_before["families"], counts_after["families"])}')
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

        logger.log(f'ERRORS ({len(errors)}):')
        for error in errors:
            logger.log(f'- {error}')

        if len(created_families) > 0:
            logger.log(f'WARNING: {len(created_families)} families were created:')
            for family_surnames in created_families:
                logger.log(f'- {family_surnames}')

    def print_stats(self):
        self.logger.log('SUMMARY')

        rows_with_data_count = self.sheet.nrows - Command.FIRST_ROW_INDEX
        self.logger.log(
            f' - Rows with data: {rows_with_data_count} (rows {Command.FIRST_ROW_INDEX + 1} to {self.sheet.nrows}). Sheet: "{self.sheet.name}"')

        self.totals = self.totalize_results()
        for class_name, states in self.totals.items():
            variation = self.get_totals_variation(class_name)
            self.logger.log(f' - {class_name} ({variation}):')

            for state, total in states.items():
                self.logger.log(f'   - {state.name}: {total}:')

        self.logger.log(f'VALIDATIONS:')

        warnings = Parent.review_data()
        for warning in warnings:
            self.logger.log(warning)

        warnings = Family.review_data()
        for warning in warnings:
            self.logger.log(warning)

        errors = self.get_errors()
        self.logger.log(f'ERRORS ({len(errors)}):')
        if len(errors) > 0:
            for error in errors:
                self.logger.error(f'- {error} ')
        else:
            self.logger.log(f'- No errors')

    def add_error(self, error):
        if error:
            self.errors.append(error)
