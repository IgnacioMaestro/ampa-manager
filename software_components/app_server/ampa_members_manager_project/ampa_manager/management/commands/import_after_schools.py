import traceback
from pathlib import Path
from typing import Optional, List

from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from ampa_manager.activity.models.after_school.after_school import AfterSchool
from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.activity.use_cases.importers.after_school_edition_importer import AfterSchoolEditionImporter
from ampa_manager.activity.use_cases.importers.after_school_importer import AfterSchoolImporter
from ampa_manager.activity.use_cases.importers.after_school_registration_importer import \
    AfterSchoolRegistrationImporter
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.parent import Parent
from ampa_manager.family.use_cases.importers.bank_account_importer import BankAccountImporter
from ampa_manager.family.use_cases.importers.child_importer import ChildImporter
from ampa_manager.family.use_cases.importers.family_importer import FamilyImporter
from ampa_manager.family.use_cases.importers.parent_importer import ParentImporter
from ampa_manager.management.commands.importers.excel_importer import ExcelImporter
from ampa_manager.management.commands.importers.excel_row import ExcelRow
from ampa_manager.management.commands.importers.import_row_result import ImportRowResult
from ampa_manager.utils.logger import Logger
from ampa_manager.utils.fields_formatters import FieldsFormatters


class Command(BaseCommand):
    help = 'Import after-schools registrations'

    SHEET_NUMBER = 0
    FIRST_ROW_INDEX = 2
    CREATE_EDITION_IF_NOT_EXISTS = True

    COLUMN_FAMILY_SURNAMES = 'family_surnames'
    COLUMN_PARENT_NAME_AND_SURNAMES = 'parent_name_and_surnames'
    COLUMN_PARENT_PHONE_NUMBER = 'parent_phone_number'
    COLUMN_PARENT_ADDITIONAL_PHONE_NUMBER = 'parent_additional_phone_number'
    COLUMN_PARENT_EMAIL = 'parent_email'
    COLUMN_BANK_ACCOUNT_SWIFT = 'bank_account_swift'
    COLUMN_BANK_ACCOUNT_IBAN = 'bank_account_iban'
    COLUMN_AFTER_SCHOOL_NAME = 'after_school_name'
    COLUMN_CHILD_NAME = 'child_name'
    COLUMN_CHILD_LEVEL = 'child_level'
    COLUMN_CHILD_YEAR_OF_BIRTH = 'child_year_of_birth'
    COLUMN_EDITION_PERIOD = 'edition_period'
    COLUMN_EDITION_TIMETABLE = 'edition_timetable'
    COLUMN_EDITION_LEVELS = 'edition_levels'
    COLUMN_EDITION_PRICE_FOR_MEMBERS = 'edition_price_for_members'
    COLUMN_EDITION_PRICE_FOR_NO_MEMBERS = 'edition_price_for_no_members'

    LABEL_FAMILY_SURNAMES = _('Family surnames')
    LABEL_PARENT_NAME_AND_SURNAMES = _('Parent name and surnames')
    LABEL_PARENT_PHONE_NUMBER = _('Parent phone number')
    LABEL_PARENT_ADDITIONAL_PHONE_NUMBER = _('Parent additional phone number')
    LABEL_PARENT_EMAIL = _('Parent email')
    LABEL_BANK_ACCOUNT_IBAN = _('Parent bank account IBAN')
    LABEL_BANK_ACCOUNT_SWIFT = _('Parent bank account SWIFT')
    LABEL_CHILD_NAME = _('Child name (without surnames)')
    LABEL_CHILD_LEVEL = _('Child level (ex. HH4, LH3)')
    LABEL_CHILD_YEAR_OF_BIRTH = _('Child year of birth (ex. 2015)')
    LABEL_AFTER_SCHOOL_NAME = _('After school name (ex. Basket)')
    LABEL_EDITION_PERIOD = _('Edition period (ex. All year)')
    LABEL_EDITION_TIMETABLE = _('Edition timetable (ex. Monday/Wednesday 17-18)')
    LABEL_EDITION_LEVELS = _('Edition levels (ex. Primary)')
    LABEL_EDITION_PRICE_FOR_MEMBERS = _('Price for members')
    LABEL_EDITION_PRICE_FOR_NO_MEMBERS = _('Price for no members')

    COLUMNS_TO_IMPORT = [
        [0, FieldsFormatters.clean_name, COLUMN_FAMILY_SURNAMES, LABEL_FAMILY_SURNAMES],
        [1, FieldsFormatters.clean_name, COLUMN_PARENT_NAME_AND_SURNAMES, LABEL_PARENT_NAME_AND_SURNAMES],
        [2, FieldsFormatters.clean_phone, COLUMN_PARENT_PHONE_NUMBER, LABEL_PARENT_PHONE_NUMBER],
        [3, FieldsFormatters.clean_phone, COLUMN_PARENT_ADDITIONAL_PHONE_NUMBER, LABEL_PARENT_ADDITIONAL_PHONE_NUMBER],
        [4, FieldsFormatters.clean_email, COLUMN_PARENT_EMAIL, LABEL_PARENT_EMAIL],
        [5, FieldsFormatters.clean_iban, COLUMN_BANK_ACCOUNT_IBAN, LABEL_BANK_ACCOUNT_IBAN],
        [6, FieldsFormatters.clean_name, COLUMN_CHILD_NAME, LABEL_CHILD_NAME],
        [7, FieldsFormatters.clean_integer, COLUMN_CHILD_YEAR_OF_BIRTH, LABEL_CHILD_YEAR_OF_BIRTH],
        [8, FieldsFormatters.clean_level, COLUMN_CHILD_LEVEL, LABEL_CHILD_LEVEL],
        [9, FieldsFormatters.clean_string, COLUMN_AFTER_SCHOOL_NAME, LABEL_AFTER_SCHOOL_NAME],
        [10, FieldsFormatters.clean_string, COLUMN_EDITION_PERIOD, LABEL_EDITION_PERIOD],
        [11, FieldsFormatters.clean_string, COLUMN_EDITION_TIMETABLE, LABEL_EDITION_TIMETABLE],
        [12, FieldsFormatters.clean_string, COLUMN_EDITION_LEVELS, LABEL_EDITION_LEVELS],
        [13, FieldsFormatters.clean_integer, COLUMN_EDITION_PRICE_FOR_MEMBERS, LABEL_EDITION_PRICE_FOR_MEMBERS],
        [14, FieldsFormatters.clean_integer, COLUMN_EDITION_PRICE_FOR_NO_MEMBERS, LABEL_EDITION_PRICE_FOR_NO_MEMBERS],
    ]

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        Command.import_after_schools_file(file_path=options['file'])

    @staticmethod
    def import_after_schools_file(file_path: str = None, file_content=None) -> Optional[List[str]]:
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
            Holder.__name__: Holder.objects.count(),
            AfterSchool.__name__: AfterSchool.objects.count(),
            AfterSchoolEdition.__name__: AfterSchoolEdition.objects.count(),
            AfterSchoolRegistration.__name__: AfterSchoolRegistration.objects.count()
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

            bank_account_result, holder_result = BankAccountImporter.import_bank_account_and_holder(parent, row.get(Command.COLUMN_BANK_ACCOUNT_IBAN))
            result.add_partial_result(bank_account_result)
            result.add_partial_result(holder_result)

            if not bank_account_result.success or not holder_result.success:
                return result
            holder = holder_result.imported_object

            after_school_result = AfterSchoolImporter.import_after_school(row.get(Command.COLUMN_AFTER_SCHOOL_NAME))
            result.add_partial_result(after_school_result)
            if not after_school_result.success:
                return result
            after_school = after_school_result.imported_object

            edition_result = AfterSchoolEditionImporter.import_edition(after_school,
                                                                       row.get(Command.COLUMN_EDITION_PERIOD),
                                                                       row.get(Command.COLUMN_EDITION_TIMETABLE),
                                                                       row.get(Command.COLUMN_EDITION_LEVELS),
                                                                       row.get(Command.COLUMN_EDITION_PRICE_FOR_MEMBERS),
                                                                       row.get(Command.COLUMN_EDITION_PRICE_FOR_NO_MEMBERS),
                                                                       Command.CREATE_EDITION_IF_NOT_EXISTS)
            result.add_partial_result(edition_result)
            if not edition_result.success:
                return result
            after_school_edition = edition_result.imported_object

            registration_result = AfterSchoolRegistrationImporter.import_registration(after_school_edition, holder, child)
            result.add_partial_result(registration_result)

        except Exception as e:
            logger.error(f'Row {row.index + 1}: {traceback.format_exc()}')
            result.error = str(e)

        return result
