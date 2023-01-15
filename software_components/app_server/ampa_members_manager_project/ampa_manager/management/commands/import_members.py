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


class ImportMembersCommand(BaseCommand):
    help = 'Import families, parents, children and bank accounts from an excel file'

    SHEET_NUMBER = 0
    FIRST_ROW_INDEX = 3

    COLUMN_FAMILY_SURNAMES = 'family_surnames'
    COLUMN_PARENT1_NAME_AND_SURNAMES = 'parent1_name_and_surnames'
    COLUMN_PARENT1_PHONE_NUMBER = 'parent1_phone_number'
    COLUMN_PARENT1_ADDITIONAL_PHONE_NUMBER = 'parent1_additional_phone_number'
    COLUMN_PARENT1_EMAIL = 'parent1_email'
    COLUMN_PARENT1_BANK_ACCOUNT_IBAN = 'parent1_bank_account_iban'
    COLUMN_PARENT1_BANK_ACCOUNT_SWIFT = 'parent1_bank_account_swift'
    COLUMN_PARENT2_NAME_AND_SURNAMES = 'parent2_name_and_surnames'
    COLUMN_PARENT2_PHONE_NUMBER = 'parent2_phone_number'
    COLUMN_PARENT2_ADDITIONAL_PHONE_NUMBER = 'parent2_additional_phone_number'
    COLUMN_PARENT2_EMAIL = 'parent2_email'
    COLUMN_CHILD1_NAME = 'child1_name'
    COLUMN_CHILD1_LEVEL = 'child1_level'
    COLUMN_CHILD1_YEAR_OF_BIRTH = 'child1_year_of_birth'
    COLUMN_CHILD2_NAME = 'child2_name'
    COLUMN_CHILD2_LEVEL = 'child2_level'
    COLUMN_CHILD2_YEAR_OF_BIRTH = 'child2_year_of_birth'
    COLUMN_CHILD3_NAME = 'child3_name'
    COLUMN_CHILD3_LEVEL = 'child3_level'
    COLUMN_CHILD3_YEAR_OF_BIRTH = 'child3_year_of_birth'
    COLUMN_CHILD4_NAME = 'child4_name'
    COLUMN_CHILD4_LEVEL = 'child4_level'
    COLUMN_CHILD4_YEAR_OF_BIRTH = 'child4_year_of_birth'
    COLUMN_CHILD5_NAME = 'child5_name'
    COLUMN_CHILD5_LEVEL = 'child5_level'
    COLUMN_CHILD5_YEAR_OF_BIRTH = 'child5_year_of_birth'

    COLUMNS_TO_IMPORT = [
        [0, FieldsFormatters.clean_name, COLUMN_FAMILY_SURNAMES],
        [1, FieldsFormatters.clean_name, COLUMN_PARENT1_NAME_AND_SURNAMES],
        [2, FieldsFormatters.clean_phone, COLUMN_PARENT1_PHONE_NUMBER],
        [3, FieldsFormatters.clean_phone, COLUMN_PARENT1_ADDITIONAL_PHONE_NUMBER],
        [4, FieldsFormatters.clean_email, COLUMN_PARENT1_EMAIL],
        [5, FieldsFormatters.clean_iban, COLUMN_PARENT1_BANK_ACCOUNT_SWIFT],
        [6, FieldsFormatters.clean_iban, COLUMN_PARENT1_BANK_ACCOUNT_IBAN],
        [8, FieldsFormatters.clean_name, COLUMN_PARENT2_NAME_AND_SURNAMES],
        [9, FieldsFormatters.clean_phone, COLUMN_PARENT2_PHONE_NUMBER],
        [10, FieldsFormatters.clean_phone, COLUMN_PARENT2_ADDITIONAL_PHONE_NUMBER],
        [11, FieldsFormatters.clean_email, COLUMN_PARENT2_EMAIL],
        [15, FieldsFormatters.clean_name, COLUMN_CHILD1_NAME],
        [16, FieldsFormatters.clean_level, COLUMN_CHILD1_LEVEL],
        [17, FieldsFormatters.clean_integer, COLUMN_CHILD1_YEAR_OF_BIRTH],
        [18, FieldsFormatters.clean_name, COLUMN_CHILD2_NAME],
        [19, FieldsFormatters.clean_level, COLUMN_CHILD2_LEVEL],
        [20, FieldsFormatters.clean_integer, COLUMN_CHILD2_YEAR_OF_BIRTH],
        [21, FieldsFormatters.clean_name, COLUMN_CHILD3_NAME],
        [22, FieldsFormatters.clean_level, COLUMN_CHILD3_LEVEL],
        [23, FieldsFormatters.clean_integer, COLUMN_CHILD3_YEAR_OF_BIRTH],
        [24, FieldsFormatters.clean_name, COLUMN_CHILD4_NAME],
        [25, FieldsFormatters.clean_level, COLUMN_CHILD4_LEVEL],
        [26, FieldsFormatters.clean_integer, COLUMN_CHILD4_YEAR_OF_BIRTH],
        [27, FieldsFormatters.clean_name, COLUMN_CHILD5_NAME],
        [28, FieldsFormatters.clean_level, COLUMN_CHILD5_LEVEL],
        [29, FieldsFormatters.clean_integer, COLUMN_CHILD5_YEAR_OF_BIRTH],
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
            for row in excel_importer.import_rows():
                result: ImportRowResult = self.import_member(row)
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
    def import_members_file(file) -> str:
        return f'not implemented: {type(file)}'

    @staticmethod
    def count_objects():
        return {
            Family.__name__: Family.objects.count(),
            Parent.__name__: Parent.objects.count(),
            Child.__name__: Child.objects.count(),
            BankAccount.__name__: BankAccount.objects.count(),
        }

    def import_member(self, row: ExcelRow) -> ImportRowResult:
        result = ImportRowResult(row.index)

        try:
            family_result = FamilyImporter.import_family(row.get(self.COLUMN_FAMILY_SURNAMES),
                                                         row.get(self.COLUMN_PARENT1_NAME_AND_SURNAMES),
                                                         row.get(self.COLUMN_PARENT2_NAME_AND_SURNAMES))
            result.add_partial_result(family_result)
            if not family_result.success:
                return result
            family = family_result.imported_object

            child1_result = ChildImporter.import_child(family,
                                                      row.get(self.COLUMN_CHILD1_NAME),
                                                      row.get(self.COLUMN_CHILD1_LEVEL),
                                                      row.get(self.COLUMN_CHILD1_YEAR_OF_BIRTH))
            result.add_partial_result(child1_result)
            if not child1_result.success:
                return result

            child2_result = ChildImporter.import_child(family,
                                                       row.get(self.COLUMN_CHILD2_NAME),
                                                       row.get(self.COLUMN_CHILD2_LEVEL),
                                                       row.get(self.COLUMN_CHILD2_YEAR_OF_BIRTH))
            result.add_partial_result(child2_result)
            if not child2_result.success:
                return result

            child3_result = ChildImporter.import_child(family,
                                                       row.get(self.COLUMN_CHILD3_NAME),
                                                       row.get(self.COLUMN_CHILD3_LEVEL),
                                                       row.get(self.COLUMN_CHILD3_YEAR_OF_BIRTH))
            result.add_partial_result(child3_result)
            if not child3_result.success:
                return result

            child4_result = ChildImporter.import_child(family,
                                                       row.get(self.COLUMN_CHILD4_NAME),
                                                       row.get(self.COLUMN_CHILD4_LEVEL),
                                                       row.get(self.COLUMN_CHILD4_YEAR_OF_BIRTH))
            result.add_partial_result(child4_result)
            if not child4_result.success:
                return result

            child5_result = ChildImporter.import_child(family,
                                                       row.get(self.COLUMN_CHILD5_NAME),
                                                       row.get(self.COLUMN_CHILD5_LEVEL),
                                                       row.get(self.COLUMN_CHILD5_YEAR_OF_BIRTH))
            result.add_partial_result(child5_result)
            if not child5_result.success:
                return result

            parent1_result = ParentImporter.import_parent(family,
                                                         row.get(self.COLUMN_PARENT1_NAME_AND_SURNAMES),
                                                         row.get(self.COLUMN_PARENT1_PHONE_NUMBER),
                                                         row.get(self.COLUMN_PARENT1_ADDITIONAL_PHONE_NUMBER),
                                                         row.get(self.COLUMN_PARENT1_EMAIL))
            result.add_partial_result(parent1_result)
            if not parent1_result.success:
                return result
            parent1 = parent1_result.imported_object

            parent2_result = ParentImporter.import_parent(family,
                                                         row.get(self.COLUMN_PARENT2_NAME_AND_SURNAMES),
                                                         row.get(self.COLUMN_PARENT2_PHONE_NUMBER),
                                                         row.get(self.COLUMN_PARENT2_ADDITIONAL_PHONE_NUMBER),
                                                         row.get(self.COLUMN_PARENT2_EMAIL))
            result.add_partial_result(parent2_result)
            if not parent2_result.success:
                return result

            bank_account_result = BankAccountImporter.import_bank_account(parent1,
                                                                          row.get(self.COLUMN_PARENT1_BANK_ACCOUNT_IBAN),
                                                                          row.get(self.COLUMN_PARENT1_BANK_ACCOUNT_SWIFT),
                                                                          True)
            result.add_partial_result(bank_account_result)
            if not bank_account_result.success:
                return result

        except Exception as e:
            self.logger.error(f'Row {row.index + 1}: {traceback.format_exc()}')
            result.error = str(e)

        return result
