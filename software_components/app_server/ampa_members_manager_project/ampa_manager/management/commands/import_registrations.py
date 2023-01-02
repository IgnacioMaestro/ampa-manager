import traceback

import xlrd
from django.core.management.base import BaseCommand

from ampa_manager.academic_course.models.level import Level
from ampa_manager.activity.models.after_school.after_school import AfterSchool
from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.parent import Parent
from ampa_manager.field_formatters.fields_formatter import FieldsFormatter
from ampa_manager.management.commands.imported_fields.registration_imported_fields import RegistrationImportedFields
from ampa_manager.management.commands.importers.child_importer import ChildImporter
from ampa_manager.management.commands.importers.parent_importer import ParentImporter
from ampa_manager.management.commands.results.import_registration_result import ImportRegistrationResult
from ampa_manager.management.commands.results.processing_state import ProcessingState


class Command(BaseCommand):
    help = 'Import after-schools registrations'

    SHEET_NUMBER = 0
    FIRST_ROW_NUMBER = 2

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

            ImportRegistrationResult.print_stats(results, counts_before, counts_after)

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
        result = ImportRegistrationResult(row_index)

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
        family_surnames = FieldsFormatter.clean_name(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_FAMILY_SURNAMES))
        child_name = FieldsFormatter.clean_name(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_CHILD_NAME))
        child_level = FieldsFormatter.parse_level(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_CHILD_LEVEL))
        child_year = FieldsFormatter.clean_integer(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_CHILD_YEAR))
        parent_name_and_surnames = FieldsFormatter.clean_name(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_PARENT_NAME_AND_SURNAMES))
        parent_phone_number = FieldsFormatter.clean_phone(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_PARENT_PHONE))
        parent_additional_phone_number = FieldsFormatter.clean_phone(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_PARENT_ADDITIONAL_PHONE))
        parent_email = FieldsFormatter.clean_email(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_PARENT_EMAIL))
        bank_account_iban = FieldsFormatter.clean_iban(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_BANK_ACCOUNT_IBAN))
        after_school_name = FieldsFormatter.clean_string(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_AFTER_SCHOOL_NAME))
        edition_timetable = FieldsFormatter.clean_string(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_EDITION_TIMETABLE))
        edition_period = FieldsFormatter.clean_string(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_EDITION_PERIOD))
        edition_levels = FieldsFormatter.clean_string(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_EDITION_LEVELS))
        edition_price_for_members = FieldsFormatter.clean_integer(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_EDITION_PRICE_FOR_MEMBERS))
        edition_price_for_no_members = FieldsFormatter.clean_integer(self.sheet.cell_value(rowx=row_index, colx=self.COLUMN_INDEX_EDITION_PRICE_FOR_NO_MEMBERS))

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
        child = family.find_child(fields.child_name)
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
        parent = family.find_parent(fields.parent_name_and_surnames)
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
