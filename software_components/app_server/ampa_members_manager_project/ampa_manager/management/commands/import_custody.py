import traceback
from pathlib import Path

from django.core.management.base import BaseCommand

from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.parent import Parent
from ampa_manager.family.use_cases.importers.bank_account_importer import BankAccountImporter
from ampa_manager.family.use_cases.importers.child_importer import ChildImporter
from ampa_manager.family.use_cases.importers.family_importer import FamilyImporter
from ampa_manager.family.use_cases.importers.parent_importer import ParentImporter
from ampa_manager.management.commands.importers.excel_importer import ExcelImporter
from ampa_manager.management.commands.importers.excel_row import ExcelRow
from ampa_manager.management.commands.importers.import_row_result import ImportRowResult
from ampa_manager.utils.fields_formatters import FieldsFormatters
from ampa_manager.utils.logger import Logger


class Command(BaseCommand):
    help = 'Import custody registrations'

    SHEET_NUMBER = 0
    FIRST_ROW_INDEX = 2
    CREATE_EDITION_IF_NOT_EXISTS = True

    COLUMN_FAMILY_SURNAMES = 'family_surnames'
    COLUMN_CHILD_NAME = 'child_name'
    COLUMN_CHILD_LEVEL = 'child_level'
    COLUMN_CHILD_YEAR_OF_BIRTH = 'child_year_of_birth'
    COLUMN_PARENT_NAME_AND_SURNAMES = 'parent_name_and_surnames'
    COLUMN_PARENT_PHONE_NUMBER = 'parent_phone_number'
    COLUMN_PARENT_ADDITIONAL_PHONE_NUMBER = 'parent_additional_phone_number'
    COLUMN_PARENT_EMAIL = 'parent_email'
    COLUMN_BANK_ACCOUNT_IBAN = 'bank_account_iban'

    COLUMNS_TO_IMPORT = [
        [0, FieldsFormatters.clean_name, COLUMN_FAMILY_SURNAMES],
        [1, FieldsFormatters.clean_name, COLUMN_CHILD_NAME],
        [3, FieldsFormatters.clean_level, COLUMN_CHILD_LEVEL],
        [4, FieldsFormatters.clean_integer, COLUMN_CHILD_YEAR_OF_BIRTH],
        [5, FieldsFormatters.clean_phone, COLUMN_PARENT_PHONE_NUMBER],
        [6, FieldsFormatters.clean_phone, COLUMN_PARENT_ADDITIONAL_PHONE_NUMBER],
        [7, FieldsFormatters.clean_email, COLUMN_PARENT_EMAIL],
        [8, FieldsFormatters.clean_name, COLUMN_PARENT_NAME_AND_SURNAMES],
        [10, FieldsFormatters.clean_iban, COLUMN_BANK_ACCOUNT_IBAN],
    ]

    def __init__(self):
        super().__init__()
        self.logger = Logger(Path(__file__).stem)

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        try:
            excel_file_name = options['file']
            excel_importer = ExcelImporter(excel_file_name, self.SHEET_NUMBER, self.FIRST_ROW_INDEX, self.COLUMNS_TO_IMPORT)

            counters_before = self.count_objects()

            results = []
            row: ExcelRow
            for row in excel_importer.get_rows():
                result: ImportRowResult = self.import_custody_registration(row)
                result.print(self.logger)
                results.append(result)

            counters_after = self.count_objects()

            ImportRowResult.print_stats(self.logger, results, counters_before, counters_after)

        except:
            self.logger.error(traceback.format_exc())
        finally:
            if self.logger:
                self.logger.close_log_file()

    @staticmethod
    def count_objects():
        return {
            Family.__name__: Family.objects.count(),
            Parent.__name__: Parent.objects.count(),
            Child.__name__: Child.objects.count(),
            BankAccount.__name__: BankAccount.objects.count(),
        }

    def import_custody_registration(self, row: ExcelRow) -> ImportRowResult:
        result = ImportRowResult(row.index)

        try:
            family_result = FamilyImporter.import_family(row.get(self.COLUMN_FAMILY_SURNAMES),
                                                         row.get(self.COLUMN_PARENT_NAME_AND_SURNAMES))
            result.add_partial_result(family_result)
            if not family_result.success:
                return result

            family = family_result.imported_object
            child_result = ChildImporter.import_child(family,
                                                      row.get(self.COLUMN_CHILD_NAME),
                                                      row.get(self.COLUMN_CHILD_LEVEL),
                                                      row.get(self.COLUMN_CHILD_YEAR_OF_BIRTH))
            result.add_partial_result(child_result)
            if not child_result.success:
                return result

            child = child_result.imported_object
            parent_result = ParentImporter.import_parent(family,
                                                         row.get(self.COLUMN_PARENT_NAME_AND_SURNAMES),
                                                         row.get(self.COLUMN_PARENT_PHONE_NUMBER),
                                                         row.get(self.COLUMN_PARENT_ADDITIONAL_PHONE_NUMBER),
                                                         row.get(self.COLUMN_PARENT_EMAIL))
            result.add_partial_result(parent_result)
            if not parent_result.success:
                return result

            parent = parent_result.imported_object
            bank_account_result = BankAccountImporter.import_bank_account(parent, row.get(self.COLUMN_BANK_ACCOUNT_IBAN))
            result.add_partial_result(bank_account_result)
            if not bank_account_result.success:
                return result

            bank_account = bank_account_result.imported_object
            # after_school_result = AfterSchoolImporter.import_after_school(row.get(self.COLUMN_AFTER_SCHOOL_NAME))
            # result.add_partial_result(after_school_result)
            # if not after_school_result.success:
            #     return result

            # after_school = after_school_result.imported_object
            # edition_result = AfterSchoolEditionImporter.import_edition(after_school,
            #                                                            row.get(self.COLUMN_EDITION_PERIOD),
            #                                                            row.get(self.COLUMN_EDITION_TIMETABLE),
            #                                                            row.get(self.COLUMN_EDITION_LEVELS),
            #                                                            row.get(self.COLUMN_EDITION_PRICE_FOR_MEMBERS),
            #                                                            row.get(self.COLUMN_EDITION_PRICE_FOR_NO_MEMBERS),
            #                                                            self.CREATE_EDITION_IF_NOT_EXISTS)
            # result.add_partial_result(edition_result)
            # if not edition_result.success:
            #     return result
            #
            # after_school_edition = edition_result.imported_object
            # registration_result = AfterSchoolRegistrationImporter.import_registration(after_school_edition, bank_account, child)
            # result.add_partial_result(registration_result)

        except Exception as e:
            self.logger.error(f'Row {row.index + 1}: {traceback.format_exc()}')
            result.error = str(e)

        return result
