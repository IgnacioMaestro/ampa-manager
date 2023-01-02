import traceback

import xlrd
from django.core.management.base import BaseCommand

from ampa_manager.academic_course.models.level import Level
from ampa_manager.activity.models.after_school.after_school import AfterSchool
from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.activity_registration.models.activity_registration import ActivityRegistration
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.parent import Parent
from ampa_manager.management.commands.import_command.importer import Importer
from ampa_manager.management.commands.import_command.importers.child_importer import ChildImporter
from ampa_manager.management.commands.import_command.importers.parent_importer import ParentImporter
from ampa_manager.management.commands.import_command.processing_state import ProcessingState


class RegistrationImportedFields:

    def __init__(self, family_surnames, child_name, child_level, child_year_of_birth, parent_name_and_surnames,
                 parent_phone_number, parent_additional_phone_number, parent_email, bank_account_iban,
                 after_school_name, edition_timetable, edition_period, edition_price_for_members,
                 edition_price_for_no_members, edition_levels):

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
        self.edition_price_for_members = edition_price_for_members
        self.edition_price_for_no_members = edition_price_for_no_members
        self.edition_levels = edition_levels

    def print(self):
        print(f' - family_surnames: {self.family_surnames} ({type(self.family_surnames)})')
        print(f' - child_name: {self.child_name} ({type(self.child_name)})')
        print(f' - child_level: {self.child_level} ({type(self.child_level)})')
        print(f' - child_year_of_birth: {self.child_year_of_birth} ({type(self.child_year_of_birth)})')
        print(f' - parent_name_and_surnames: {self.parent_name_and_surnames} ({type(self.parent_name_and_surnames)})')
        print(f' - parent_phone_number: {self.parent_phone_number} ({type(self.parent_phone_number)})')
        print(f' - parent_additional_phone_number: {self.parent_additional_phone_number} ({type(self.parent_additional_phone_number)})')
        print(f' - parent_email: {self.parent_email} ({type(self.parent_email)})')
        print(f' - bank_account_iban: {self.bank_account_iban} ({type(self.bank_account_iban)})')
        print(f' - after_school_name: {self.after_school_name} ({type(self.after_school_name)})')
        print(f' - edition_timetable: {self.edition_timetable} ({type(self.edition_timetable)})')
        print(f' - edition_period: {self.edition_period} ({type(self.edition_period)})')
        print(f' - edition_price_for_members: {self.edition_price_for_members} ({type(self.edition_price_for_members)})')
        print(f' - edition_price_for_no_members: {self.edition_price_for_no_members} ({type(self.edition_price_for_no_members)})')
        print(f' - edition_levels: {self.edition_levels} ({type(self.edition_levels)})')

    def get_list(self):
        return [self.family_surnames, self.child_name, self.child_level, self.child_year_of_birth,
                self.parent_name_and_surnames, self.parent_phone_number, self.parent_additional_phone_number,
                self.parent_email, self.bank_account_iban, self.after_school_name, self.edition_timetable,
                self.edition_period, self.edition_price_for_members, self.edition_price_for_no_members, self.edition_levels]


class ImportResult:

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


class Command(BaseCommand):
    help = 'Import activity registrations'

    SHEET_NUMBER = 0
    FIRST_ROW_NUMBER = 2

    FAMILY_SURNAMES_INDEX = 0
    CHILD_NAME_INDEX = 1
    CHILD_LEVEL_INDEX = 3
    CHILD_YEAR_INDEX = 4
    PARENT_PHONE_INDEX = 5
    PARENT_ADDITIONAL_PHONE_INDEX = 6
    PARENT_EMAIL_INDEX = 7
    PARENT_NAME_AND_SURNAMES_INDEX = 8
    BANK_ACCOUNT_IBAN_INDEX = 10
    AFTER_SCHOOL_NAME_INDEX = 11
    EDITION_PERIOD_INDEX = 12
    EDITION_TIMETABLE_INDEX = 13
    EDITION_LEVELS_INDEX = 14
    EDITION_PRICE_FOR_MEMBERS_INDEX = 15
    EDITION_PRICE_FOR_NO_MEMBERS_INDEX = 16

    CREATE_EDITION_IF_NOT_EXISTS = True

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        try:
            self.load_excel(options['file'])
            counts_before = Command.count_objects()

            results = []
            for row_index in range(Command.FIRST_ROW_NUMBER, self.sheet.nrows):
                result = self.import_row(row_index)
                result.print()
                results.append(result)

            counts_after = Command.count_objects()

            ImportResult.print_stats(results, counts_before, counts_after)

        except:
            print(traceback.format_exc())
    @staticmethod
    def count_objects():
        return {
            'families': Family.objects.count(),
            'parents': Parent.objects.count(),
            'children': Child.objects.count(),
            'bank_accounts': BankAccount.objects.count(),
            'after_schools': AfterSchool.objects.count(),
            'editions': AfterSchoolEdition.objects.count(),
            'registrations': AfterSchoolRegistration.objects.count()
        }

    def import_row(self, row_index):
        result = ImportResult(row_index)

        try:
            result.fields = self.import_fields(row_index)

            family, result.family_state, result.error = Command.import_family(result.fields)
            if family:

                child, result.child_state, result.error = Command.import_child(family, result.fields)
                if child:

                    parent, result.parent_state, result.error = Command.import_parent(family, result.fields)
                    if parent:

                        bank_account, result.bank_account_state, result.error = Command.import_bank_account(parent, result.fields)
                        if bank_account:

                            after_school, result.after_school_state, result.error = Command.import_after_school(result.fields)
                            if after_school:

                                after_school_edition, result.edition_state, result.error = Command.import_after_school_edition(
                                    after_school, result.fields)
                                if after_school_edition:
                                    result.registration, result.registration_state = Command.import_registration(
                                        after_school_edition, bank_account, child)
        except Exception as e:
            print(f'Row {row_index + 1}: {traceback.format_exc()}')
            result.error = str(e)

        return result

    def load_excel(self, file_path):
        print(f'\nImporting file {file_path}')
        self.book = xlrd.open_workbook(file_path)
        self.sheet = self.book.sheet_by_index(Command.SHEET_NUMBER)

    def import_fields(self, row_index):
        family_surnames = Importer.clean_surname(self.sheet.cell_value(rowx=row_index, colx=self.FAMILY_SURNAMES_INDEX))
        child_name = Importer.clean_surname(self.sheet.cell_value(rowx=row_index, colx=self.CHILD_NAME_INDEX))
        child_level = Level.parse_level(self.sheet.cell_value(rowx=row_index, colx=self.CHILD_LEVEL_INDEX))
        child_year = Importer.clean_integer(self.sheet.cell_value(rowx=row_index, colx=self.CHILD_YEAR_INDEX))
        parent_name_and_surnames = Importer.clean_surname(
            self.sheet.cell_value(rowx=row_index, colx=self.PARENT_NAME_AND_SURNAMES_INDEX))
        parent_phone_number = Importer.clean_phone(self.sheet.cell_value(rowx=row_index, colx=self.PARENT_PHONE_INDEX))
        parent_additional_phone_number = Importer.clean_phone(self.sheet.cell_value(rowx=row_index, colx=self.PARENT_ADDITIONAL_PHONE_INDEX))
        parent_email = Importer.clean_email(self.sheet.cell_value(rowx=row_index, colx=self.PARENT_EMAIL_INDEX))
        bank_account_iban = Importer.clean_string(self.sheet.cell_value(rowx=row_index, colx=self.BANK_ACCOUNT_IBAN_INDEX))
        after_school_name = Importer.clean_string(self.sheet.cell_value(rowx=row_index, colx=self.AFTER_SCHOOL_NAME_INDEX))
        edition_timetable = Importer.clean_string(self.sheet.cell_value(rowx=row_index, colx=self.EDITION_TIMETABLE_INDEX))
        edition_period = Importer.clean_string(self.sheet.cell_value(rowx=row_index, colx=self.EDITION_PERIOD_INDEX))
        edition_levels = Importer.clean_string(self.sheet.cell_value(rowx=row_index, colx=self.EDITION_LEVELS_INDEX))
        edition_price_for_members = Importer.clean_integer(self.sheet.cell_value(rowx=row_index, colx=self.EDITION_PRICE_FOR_MEMBERS_INDEX))
        edition_price_for_no_members = Importer.clean_integer(self.sheet.cell_value(rowx=row_index, colx=self.EDITION_PRICE_FOR_NO_MEMBERS_INDEX))

        return RegistrationImportedFields(family_surnames, child_name, child_level, child_year,
                                          parent_name_and_surnames, parent_phone_number, parent_additional_phone_number,
                                          parent_email, bank_account_iban, after_school_name, edition_timetable,
                                          edition_period, edition_price_for_members, edition_price_for_no_members, edition_levels)

    @staticmethod
    def import_family(fields):
        family, error = Family.find(fields.family_surnames, fields.parent_name_and_surnames)

        if family:
            state = ProcessingState.NOT_MODIFIED
        elif error:
            state = ProcessingState.ERROR
        elif fields.family_surnames:
            family = Family.objects.create(surnames=fields.family_surnames)
            state = ProcessingState.CREATED
        else:
            state = ProcessingState.ERROR
            error = 'Family error: Missing surnames'

        return family, state, error

    @staticmethod
    def import_child(family, fields):
        child = Child.find(family, fields.child_name)
        error = None

        repetition = Level.calculate_repetition(fields.child_level, fields.child_year_of_birth)
        if child:
            if ChildImporter.is_modified(child, fields.child_year_of_birth, repetition):
                ChildImporter.update(child, fields.child_year_of_birth, repetition)
                state = ProcessingState.UPDATED
            else:
                state = ProcessingState.NOT_MODIFIED
        else:
            fields_ok, error = ChildImporter.validate_fields(fields.child_name, fields.child_year_of_birth, repetition)
            if fields_ok:
                child = Child.objects.create(name=fields.child_name, year_of_birth=fields.child_year_of_birth,
                                             repetition=repetition, family=family)
                state = ProcessingState.CREATED
            else:
                state = ProcessingState.ERROR

        return child, state, f'Child error: {error}'

    @staticmethod
    def import_parent(family, fields):
        parent = Parent.find(family, fields.parent_name_and_surnames)
        error = None

        if parent:
            if ParentImporter.is_modified(parent, fields.parent_phone_number, fields.parent_additional_phone_number,
                                          fields.parent_email):
                ParentImporter.update(parent, fields.parent_phone_number, fields.parent_additional_phone_number,
                                      fields.parent_email)
                state = ProcessingState.UPDATED
            else:
                state = ProcessingState.NOT_MODIFIED
        else:
            fields_ok, error = ParentImporter.validate_fields(fields.parent_name_and_surnames,
                                                              fields.parent_phone_number,
                                                              fields.parent_additional_phone_number,
                                                              fields.parent_email)
            if fields_ok:
                parent = Parent.objects.create(name_and_surnames=fields.parent_name_and_surnames,
                                               phone_number=fields.parent_phone_number,
                                               additional_phone_number=fields.parent_additional_phone_number,
                                               email=fields.parent_email)
                family.parents.add(parent)
                state = ProcessingState.CREATED
            else:
                state = ProcessingState.ERROR

        return parent, state, f'Parent error: {error}'

    @staticmethod
    def import_bank_account(parent, fields):
        bank_account = BankAccount.find(fields.bank_account_iban)
        error = None

        if bank_account:
            state = ProcessingState.NOT_MODIFIED
        elif fields.bank_account_iban:
            bank_account = BankAccount.objects.create(iban=fields.bank_account_iban, owner=parent)
            state = ProcessingState.CREATED
        else:
            state = ProcessingState.ERROR
            error = 'Missing IBAN'

        return bank_account, state, f'Bank account error: {error}'

    @staticmethod
    def import_after_school(fields):
        after_school = AfterSchool.find(fields.after_school_name)
        if after_school:
            return after_school, ProcessingState.NOT_MODIFIED, None
        else:
            return None, ProcessingState.ERROR, f'After-school error: not found "{fields.after_school_name}"'

    @staticmethod
    def import_after_school_edition(after_school, fields):
        edition = AfterSchoolEdition.find_edition_for_active_course(after_school, fields.edition_period,
                                                                    fields.edition_timetable, fields.edition_levels)
        if edition:
            return edition, ProcessingState.NOT_MODIFIED, None
        elif Command.CREATE_EDITION_IF_NOT_EXISTS:
            edition = AfterSchoolEdition.create_edition_for_active_course(after_school, fields.edition_period,
                                                        fields.edition_timetable, fields.edition_levels,
                                                        fields.edition_price_for_members,
                                                        fields.edition_price_for_no_members)
            return edition, ProcessingState.CREATED, None
        else:
            return None, ProcessingState.ERROR, f'Activity error: not found "{fields.activity_period_name}"'

    @staticmethod
    def import_registration(after_school_edition, bank_account, child):
        registration = AfterSchoolRegistration.find(after_school_edition, child)
        if registration:
            if registration.bank_account != bank_account:
                registration.bank_account = bank_account
                registration.save()
                return registration, ProcessingState.UPDATED
            else:
                return registration, ProcessingState.NOT_MODIFIED
        else:
            registration = AfterSchoolRegistration.objects.create(after_school_edition=after_school_edition,
                                                                  bank_account=bank_account, child=child)
            return registration, ProcessingState.CREATED
