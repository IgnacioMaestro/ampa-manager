import traceback
from pathlib import Path
from typing import List, Optional

from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _

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

    FAMILY_FIELDS = [COLUMN_FAMILY_SURNAMES]
    PARENT1_FIELDS = [
        COLUMN_PARENT1_NAME_AND_SURNAMES,
        COLUMN_PARENT1_PHONE_NUMBER,
        COLUMN_PARENT1_ADDITIONAL_PHONE_NUMBER,
        COLUMN_PARENT1_EMAIL,
    ]
    PARENT2_FIELDS = [
        COLUMN_PARENT2_NAME_AND_SURNAMES,
        COLUMN_PARENT2_PHONE_NUMBER,
        COLUMN_PARENT2_PHONE_NUMBER,
        COLUMN_PARENT2_ADDITIONAL_PHONE_NUMBER
    ]
    CHILD1_FIELDS = [
        COLUMN_CHILD1_NAME,
        COLUMN_CHILD1_LEVEL,
        COLUMN_CHILD1_YEAR_OF_BIRTH
    ]
    CHILD2_FIELDS = [
        COLUMN_CHILD2_NAME,
        COLUMN_CHILD2_LEVEL,
        COLUMN_CHILD2_YEAR_OF_BIRTH
    ]
    CHILD3_FIELDS = [
        COLUMN_CHILD3_NAME,
        COLUMN_CHILD3_LEVEL,
        COLUMN_CHILD3_YEAR_OF_BIRTH
    ]
    CHILD4_FIELDS = [
        COLUMN_CHILD4_NAME,
        COLUMN_CHILD4_LEVEL,
        COLUMN_CHILD4_YEAR_OF_BIRTH
    ]
    CHILD5_FIELDS = [
        COLUMN_CHILD5_NAME,
        COLUMN_CHILD5_LEVEL,
        COLUMN_CHILD5_YEAR_OF_BIRTH
    ]
    PARENT1_BANK_ACCOUNT_FIELDS = [
        COLUMN_PARENT1_BANK_ACCOUNT_IBAN,
        COLUMN_PARENT1_BANK_ACCOUNT_SWIFT
    ]

    LABEL_FAMILY_SURNAMES = _('Family') + ': ' + _('Surnames')
    LABEL_PARENT1_NAME_AND_SURNAMES = _('Parent %(number)s') % {'number': 1} + ': ' + _('Name and surnames')
    LABEL_PARENT1_PHONE_NUMBER = _('Parent %(number)s') % {'number': 1} + ': ' + _('Phone number')
    LABEL_PARENT1_ADDITIONAL_PHONE_NUMBER = _('Parent %(number)s')  % {'number': 1} + ': ' + _('Additional phone number')
    LABEL_PARENT1_EMAIL = _('Parent %(number)s') % {'number': 1} + ': ' + _('Email')
    LABEL_PARENT1_BANK_ACCOUNT_IBAN = _('Parent %(number)s') % {'number': 1} + ': ' + _('Bank account IBAN')
    LABEL_PARENT1_BANK_ACCOUNT_SWIFT = _('Parent %(number)s') % {'number': 1} + ': ' + _('Bank account SWIFT')
    LABEL_PARENT2_NAME_AND_SURNAMES = _('Parent %(number)s') % {'number': 2} + ': ' + _('Name and surnames')
    LABEL_PARENT2_PHONE_NUMBER = _('Parent %(number)s') % {'number': 2} + ': ' + _('Phone number')
    LABEL_PARENT2_ADDITIONAL_PHONE_NUMBER = _('Parent %(number)s')  % {'number': 2} + ': ' + _('Additional phone number')
    LABEL_PARENT2_EMAIL = _('Parent %(number)s') % {'number': 2} + ': ' + _('Email')
    LABEL_CHILD1_NAME = _('Child %(number)s') % {'number': 1} + ': ' + _('Name (without surnames)')
    LABEL_CHILD1_LEVEL = _('Child %(number)s') % {'number': 1} + ': ' + _('Level (ex. HH4, LH3)')
    LABEL_CHILD1_YEAR_OF_BIRTH = _('Child %(number)s') % {'number': 1} + ': ' + _('Year of birth (ex. 2015)')
    LABEL_CHILD2_NAME = _('Child %(number)s') % {'number': 2} + ': ' + _('Name (without surnames)')
    LABEL_CHILD2_LEVEL = _('Child %(number)s') % {'number': 2} + ': ' + _('Level (ex. HH4, LH3)')
    LABEL_CHILD2_YEAR_OF_BIRTH = _('Child %(number)s')  % {'number': 2} + ': ' + _('Year of birth (ex. 2015)')
    LABEL_CHILD3_NAME = _('Child %(number)s') % {'number': 3} + ': ' + _('Name (without surnames)')
    LABEL_CHILD3_LEVEL = _('Child %(number)s') % {'number': 3} + ': ' + _('Level (ex. HH4, LH3)')
    LABEL_CHILD3_YEAR_OF_BIRTH = _('Child %(number)s') % {'number': 3} + ': ' + _('Year of birth (ex. 2015)')
    LABEL_CHILD4_NAME = _('Child %(number)s') % {'number': 4} + ': ' + _('Name (without surnames)')
    LABEL_CHILD4_LEVEL = _('Child %(number)s') % {'number': 4} + ': ' + _('Level (ex. HH4, LH3)')
    LABEL_CHILD4_YEAR_OF_BIRTH = _('Child %(number)s') % {'number': 4} + ': ' + _('Year of birth (ex. 2015)')
    LABEL_CHILD5_NAME = _('Child %(number)s') % {'number': 5} + ': ' + _('Name (without surnames)')
    LABEL_CHILD5_LEVEL = _('Child %(number)s') % {'number': 5} + ': ' + _('Level (ex. HH4, LH3)')
    LABEL_CHILD5_YEAR_OF_BIRTH = _('Child %(number)s') % {'number': 5} + ': ' + _('Year of birth (ex. 2015)')

    COLUMNS_TO_IMPORT = [
        [0, FieldsFormatters.clean_name, COLUMN_FAMILY_SURNAMES, LABEL_FAMILY_SURNAMES],
        [1, FieldsFormatters.clean_name, COLUMN_PARENT1_NAME_AND_SURNAMES, LABEL_PARENT1_NAME_AND_SURNAMES],
        [2, FieldsFormatters.clean_phone, COLUMN_PARENT1_PHONE_NUMBER, LABEL_PARENT1_PHONE_NUMBER],
        [3, FieldsFormatters.clean_phone, COLUMN_PARENT1_ADDITIONAL_PHONE_NUMBER, LABEL_PARENT1_ADDITIONAL_PHONE_NUMBER],
        [4, FieldsFormatters.clean_email, COLUMN_PARENT1_EMAIL, LABEL_PARENT1_EMAIL],
        [5, FieldsFormatters.clean_iban, COLUMN_PARENT1_BANK_ACCOUNT_SWIFT, LABEL_PARENT1_BANK_ACCOUNT_SWIFT],
        [6, FieldsFormatters.clean_iban, COLUMN_PARENT1_BANK_ACCOUNT_IBAN, LABEL_PARENT1_BANK_ACCOUNT_IBAN],
        [7, FieldsFormatters.clean_name, COLUMN_PARENT2_NAME_AND_SURNAMES, LABEL_PARENT2_NAME_AND_SURNAMES],
        [8, FieldsFormatters.clean_phone, COLUMN_PARENT2_PHONE_NUMBER, LABEL_PARENT2_PHONE_NUMBER],
        [9, FieldsFormatters.clean_phone, COLUMN_PARENT2_ADDITIONAL_PHONE_NUMBER, LABEL_PARENT2_ADDITIONAL_PHONE_NUMBER],
        [10, FieldsFormatters.clean_email, COLUMN_PARENT2_EMAIL, LABEL_PARENT2_EMAIL],
        [11, FieldsFormatters.clean_name, COLUMN_CHILD1_NAME, LABEL_CHILD1_NAME],
        [12, FieldsFormatters.clean_integer, COLUMN_CHILD1_YEAR_OF_BIRTH, LABEL_CHILD1_YEAR_OF_BIRTH],
        [13, FieldsFormatters.clean_level, COLUMN_CHILD1_LEVEL, LABEL_CHILD1_LEVEL],
        [14, FieldsFormatters.clean_name, COLUMN_CHILD2_NAME, LABEL_CHILD2_NAME],
        [15, FieldsFormatters.clean_integer, COLUMN_CHILD2_YEAR_OF_BIRTH, LABEL_CHILD2_YEAR_OF_BIRTH],
        [16, FieldsFormatters.clean_level, COLUMN_CHILD2_LEVEL, LABEL_CHILD2_LEVEL],
        [17, FieldsFormatters.clean_name, COLUMN_CHILD3_NAME, LABEL_CHILD3_NAME],
        [18, FieldsFormatters.clean_integer, COLUMN_CHILD3_YEAR_OF_BIRTH, LABEL_CHILD3_YEAR_OF_BIRTH],
        [19, FieldsFormatters.clean_level, COLUMN_CHILD3_LEVEL, LABEL_CHILD3_LEVEL],
        [20, FieldsFormatters.clean_name, COLUMN_CHILD4_NAME, LABEL_CHILD4_NAME],
        [21, FieldsFormatters.clean_integer, COLUMN_CHILD4_YEAR_OF_BIRTH, LABEL_CHILD4_YEAR_OF_BIRTH],
        [22, FieldsFormatters.clean_level, COLUMN_CHILD4_LEVEL, LABEL_CHILD4_LEVEL],
        [23, FieldsFormatters.clean_name, COLUMN_CHILD5_NAME, LABEL_CHILD5_NAME],
        [24, FieldsFormatters.clean_integer, COLUMN_CHILD5_YEAR_OF_BIRTH, LABEL_CHILD5_YEAR_OF_BIRTH],
        [25, FieldsFormatters.clean_level, COLUMN_CHILD5_LEVEL, LABEL_CHILD5_LEVEL],
    ]

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        Command.import_members_file(file_path=options['file'])

    @staticmethod
    def import_members_file(file_path: str = None, file_content=None) -> Optional[List[str]]:
        logger = None
        try:
            logger = Logger(Path(__file__).stem)

            excel_importer = ExcelImporter(Command.SHEET_NUMBER,
                                           Command.FIRST_ROW_INDEX,
                                           Command.COLUMNS_TO_IMPORT,
                                           file_path=file_path,
                                           file_content=file_content)

            counters_before = Command.count_objects()

            results = []
            row: ExcelRow
            for row in excel_importer.get_rows():
                result: ImportRowResult = Command.import_row(row, logger)
                result.print(logger)
                results.append(result)

            counters_after = Command.count_objects()

            ImportRowResult.print_stats(logger, results, counters_before, counters_after)

        except:
            logger.error(traceback.format_exc())
        finally:
            if logger:
                logger.close_log_file()

        if logger:
            return logger.logs
        else:
            return None

    @staticmethod
    def count_objects():
        return {
            Family.__name__: Family.objects.count(),
            Parent.__name__: Parent.objects.count(),
            Child.__name__: Child.objects.count(),
            BankAccount.__name__: BankAccount.objects.count(),
        }

    @staticmethod
    def import_row(row: ExcelRow, logger: Logger) -> ImportRowResult:
        result = ImportRowResult(row.index)

        try:
            family_result = FamilyImporter.import_family(row.get(Command.COLUMN_FAMILY_SURNAMES),
                                                         row.get(Command.COLUMN_PARENT1_NAME_AND_SURNAMES),
                                                         row.get(Command.COLUMN_PARENT2_NAME_AND_SURNAMES))
            result.add_partial_result(family_result)
            if not family_result.success:
                return result
            family = family_result.imported_object

            result = Command.import_children(row, family, result)
            result = Command.import_parents(row, family, result)

        except Exception as e:
            logger.error(f'Row {row.index + 1}: {traceback.format_exc()}')
            result.error = str(e)

        return result

    @staticmethod
    def import_children(row: ExcelRow, family, result: ImportRowResult):

        if row.any_column_has_value(Command.CHILD1_FIELDS):
            child1_result = ChildImporter.import_child(family,
                                                       row.get(Command.COLUMN_CHILD1_NAME),
                                                       row.get(Command.COLUMN_CHILD1_LEVEL),
                                                       row.get(Command.COLUMN_CHILD1_YEAR_OF_BIRTH))
            result.add_partial_result(child1_result)
            if not child1_result.success:
                return result

        if row.any_column_has_value(Command.CHILD2_FIELDS):
            child2_result = ChildImporter.import_child(family,
                                                       row.get(Command.COLUMN_CHILD2_NAME),
                                                       row.get(Command.COLUMN_CHILD2_LEVEL),
                                                       row.get(Command.COLUMN_CHILD2_YEAR_OF_BIRTH))
            result.add_partial_result(child2_result)
            if not child2_result.success:
                return result

        if row.any_column_has_value(Command.CHILD3_FIELDS):
            child3_result = ChildImporter.import_child(family,
                                                       row.get(Command.COLUMN_CHILD3_NAME),
                                                       row.get(Command.COLUMN_CHILD3_LEVEL),
                                                       row.get(Command.COLUMN_CHILD3_YEAR_OF_BIRTH))
            result.add_partial_result(child3_result)
            if not child3_result.success:
                return result

        if row.any_column_has_value(Command.CHILD4_FIELDS):
            child4_result = ChildImporter.import_child(family,
                                                       row.get(Command.COLUMN_CHILD4_NAME),
                                                       row.get(Command.COLUMN_CHILD4_LEVEL),
                                                       row.get(Command.COLUMN_CHILD4_YEAR_OF_BIRTH))
            result.add_partial_result(child4_result)
            if not child4_result.success:
                return result

        if row.any_column_has_value(Command.CHILD5_FIELDS):
            child5_result = ChildImporter.import_child(family,
                                                       row.get(Command.COLUMN_CHILD5_NAME),
                                                       row.get(Command.COLUMN_CHILD5_LEVEL),
                                                       row.get(Command.COLUMN_CHILD5_YEAR_OF_BIRTH))
            result.add_partial_result(child5_result)
            if not child5_result.success:
                return result

        return result

    @staticmethod
    def import_parents(row: ExcelRow, family, result: ImportRowResult):
        if row.any_column_has_value(Command.PARENT1_FIELDS):
            parent1_result = ParentImporter.import_parent(family,
                                                          row.get(Command.COLUMN_PARENT1_NAME_AND_SURNAMES),
                                                          row.get(Command.COLUMN_PARENT1_PHONE_NUMBER),
                                                          row.get(Command.COLUMN_PARENT1_ADDITIONAL_PHONE_NUMBER),
                                                          row.get(Command.COLUMN_PARENT1_EMAIL))
            result.add_partial_result(parent1_result)
            if not parent1_result.success:
                return result
            parent1 = parent1_result.imported_object

            if row.any_column_has_value(Command.PARENT1_BANK_ACCOUNT_FIELDS):
                bank_account_result = BankAccountImporter.import_bank_account(parent1,
                                                                              row.get(Command.COLUMN_PARENT1_BANK_ACCOUNT_IBAN),
                                                                              row.get(Command.COLUMN_PARENT1_BANK_ACCOUNT_SWIFT),
                                                                              True)
                result.add_partial_result(bank_account_result)
                if not bank_account_result.success:
                    return result

        if row.any_column_has_value(Command.PARENT2_FIELDS):
            parent2_result = ParentImporter.import_parent(family,
                                                          row.get(Command.COLUMN_PARENT2_NAME_AND_SURNAMES),
                                                          row.get(Command.COLUMN_PARENT2_PHONE_NUMBER),
                                                          row.get(Command.COLUMN_PARENT2_ADDITIONAL_PHONE_NUMBER),
                                                          row.get(Command.COLUMN_PARENT2_EMAIL))
            result.add_partial_result(parent2_result)
            if not parent2_result.success:
                return result

        return result