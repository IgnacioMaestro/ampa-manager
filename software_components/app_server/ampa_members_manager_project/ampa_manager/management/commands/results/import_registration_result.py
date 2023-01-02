from ampa_manager.management.commands.results.processing_state import ProcessingState
from ampa_manager.management.commands.imported_fields.registration_imported_fields import RegistrationImportedFields


class ImportRegistrationResult:

    def __init__(self, row_index):
        self.row_index = row_index
        self.fields = RegistrationImportedFields(None, None, None, None, None, None, None, None, None, None, None, None,
                                                 None, None, None)
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

        print(f'\nFAMILIES {counts_before["families"]} -> {counts_after["families"]}')
        for state, total in family_totals.items():
            print(f'- {state.name}: {total}')

        print(f'CHILDREN {counts_before["children"]} -> {counts_after["children"]}')
        for state, total in child_totals.items():
            print(f'- {state.name}: {total}')

        print(f'PARENTS {counts_before["parents"]} -> {counts_after["parents"]}')
        for state, total in parent_totals.items():
            print(f'- {state.name}: {total}')

        print(f'BANK ACCOUNTS {counts_before["bank_accounts"]} -> {counts_after["bank_accounts"]}')
        for state, total in bank_account_totals.items():
            print(f'- {state.name}: {total}')

        print(f'AFTER SCHOOLS {counts_before["after_schools"]} -> {counts_after["after_schools"]}')
        for state, total in after_school_totals.items():
            print(f'- {state.name}: {total}')

        print(f'EDITIONS {counts_before["editions"]} -> {counts_after["editions"]}')
        for state, total in edition_totals.items():
            print(f'- {state.name}: {total}')

        print(f'REGISTRATIONS {counts_before["registrations"]} -> {counts_after["registrations"]}')
        for state, total in registration_totals.items():
            print(f'- {state.name}: {total}')

        print(f'\nERRORS ({len(errors)}):')
        for error in errors:
            print(f'- {error}')

        if len(created_families) > 0:
            print(f'\nWARNING: {len(created_families)} families were created:')
            for family_surnames in created_families:
                print(f'- {family_surnames}')