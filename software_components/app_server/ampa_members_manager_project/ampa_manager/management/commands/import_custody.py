import traceback
from pathlib import Path
from typing import Optional, List

from django.core.management.base import BaseCommand

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.activity.use_cases.importers.custody_edition_importer import CustodyEditionImporter
from ampa_manager.activity.use_cases.importers.custody_registration_importer import CustodyRegistrationImporter
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

    COLUMN_FAMILY_SURNAMES = 'family_surnames'
    COLUMN_FAMILY_IS_MEMBER = 'family_is_member'
    COLUMN_PARENT_NAME_AND_SURNAMES = 'parent_name_and_surnames'
    COLUMN_PARENT_PHONE_NUMBER = 'parent_phone_number'
    COLUMN_PARENT_ADDITIONAL_PHONE_NUMBER = 'parent_additional_phone_number'
    COLUMN_PARENT_EMAIL = 'parent_email'
    COLUMN_BANK_ACCOUNT_IBAN = 'bank_account_iban'
    COLUMN_CHILD_NAME = 'child_name'
    COLUMN_CHILD_LEVEL = 'child_level'
    COLUMN_CHILD_YEAR_OF_BIRTH = 'child_year_of_birth'
    COLUMN_EDITION1_ASSISTED_DAYS = 'edition1_assisted_days'
    COLUMN_EDITION2_ASSISTED_DAYS = 'edition2_assisted_days'
    COLUMN_EDITION3_ASSISTED_DAYS = 'edition3_assisted_days'
    COLUMN_EDITION4_ASSISTED_DAYS = 'edition4_assisted_days'
    COLUMN_EDITION5_ASSISTED_DAYS = 'edition5_assisted_days'
    COLUMN_EDITION6_ASSISTED_DAYS = 'edition6_assisted_days'

    COLUMNS_TO_IMPORT = [
        [0, FieldsFormatters.clean_name, COLUMN_FAMILY_SURNAMES],
        [1, FieldsFormatters.clean_phone, COLUMN_PARENT_PHONE_NUMBER],
        [2, FieldsFormatters.clean_phone, COLUMN_PARENT_ADDITIONAL_PHONE_NUMBER],
        [3, FieldsFormatters.clean_email, COLUMN_PARENT_EMAIL],
        [4, FieldsFormatters.clean_name, COLUMN_PARENT_NAME_AND_SURNAMES],
        [5, FieldsFormatters.clean_iban, COLUMN_BANK_ACCOUNT_IBAN],
        [6, FieldsFormatters.clean_name, COLUMN_CHILD_NAME],
        [7, FieldsFormatters.clean_level, COLUMN_CHILD_LEVEL],
        [8, FieldsFormatters.clean_integer, COLUMN_CHILD_YEAR_OF_BIRTH],
        [9, FieldsFormatters.clean_integer, COLUMN_EDITION1_ASSISTED_DAYS],
        [10, FieldsFormatters.clean_integer, COLUMN_EDITION2_ASSISTED_DAYS],
        [11, FieldsFormatters.clean_integer, COLUMN_EDITION3_ASSISTED_DAYS],
        [12, FieldsFormatters.clean_integer, COLUMN_EDITION4_ASSISTED_DAYS],
        [13, FieldsFormatters.clean_integer, COLUMN_EDITION5_ASSISTED_DAYS],
        [14, FieldsFormatters.clean_integer, COLUMN_EDITION6_ASSISTED_DAYS],
    ]

    def __init__(self):
        super().__init__()
        self.logger = Logger(Path(__file__).stem)

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    @staticmethod
    def import_custody_file(file_path: str = None, file_content=None) -> Optional[List[str]]:
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
            CustodyRegistration.__name__: CustodyRegistration.objects.count(),
        }

    @staticmethod
    def import_row(row: ExcelRow, logger: Logger) -> ImportRowResult:
        result = ImportRowResult(row.index)

        try:
            family_result = FamilyImporter.import_family(row.get(Command.COLUMN_FAMILY_SURNAMES),
                                                         row.get(Command.COLUMN_PARENT_NAME_AND_SURNAMES))
            result.add_partial_result(family_result)
            if not family_result.success:
                return result
            family = family_result.imported_object

            child_result = ChildImporter.import_child(family,
                                                      row.get(Command.COLUMN_CHILD_NAME),
                                                      row.get(Command.COLUMN_CHILD_LEVEL),
                                                      row.get(Command.COLUMN_CHILD_YEAR_OF_BIRTH))
            result.add_partial_result(child_result)
            if not child_result.success:
                return result
            child = child_result.imported_object

            parent_result = ParentImporter.import_parent(family,
                                                         row.get(Command.COLUMN_PARENT_NAME_AND_SURNAMES),
                                                         row.get(Command.COLUMN_PARENT_PHONE_NUMBER),
                                                         row.get(Command.COLUMN_PARENT_ADDITIONAL_PHONE_NUMBER),
                                                         row.get(Command.COLUMN_PARENT_EMAIL))
            result.add_partial_result(parent_result)
            if not parent_result.success:
                return result
            parent = parent_result.imported_object

            bank_account_result, holder_result = BankAccountImporter.import_bank_account_and_holder(parent, row.get(
                Command.COLUMN_BANK_ACCOUNT_IBAN))
            result.add_partial_result(bank_account_result)
            result.add_partial_result(holder_result)

            if not bank_account_result.success or not holder_result.success:
                return result
            holder = holder_result.imported_object

            academic_course: AcademicCourse = ActiveCourse.load()
            edition_result = CustodyEditionImporter.import_custody_edition(academic_course, edition_period, child.cycle)
            result.add_partial_result(edition_result)
            if not edition_result.success:
                return result
            custody_edition = edition_result.imported_object

            registration_result = CustodyRegistrationImporter.import_registration(custody_edition, holder, child,
                                                                                  row.get(Command.COLUMN_EDITION1_ASSISTED_DAYS))
            result.add_partial_result(registration_result)

        except Exception as e:
            logger.error(f'Row {row.index + 1}: {traceback.format_exc()}')
            result.error = str(e)

        return result
