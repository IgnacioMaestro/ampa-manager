import traceback
from pathlib import Path
from typing import Optional, List

from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.after_school.after_school import AfterSchool
from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.activity.use_cases.importers.after_school_edition_importer import AfterSchoolEditionImporter
from ampa_manager.activity.use_cases.importers.after_school_importer import AfterSchoolImporter
from ampa_manager.activity.use_cases.importers.after_school_registration_importer import AfterSchoolRegistrationImporter
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
from ampa_manager.utils.fields_formatters import FieldsFormatters
from ampa_manager.utils.logger import Logger


class AfterSchoolsActivitiesImporter:
    SHEET_NUMBER = 0
    FIRST_ROW_INDEX = 2

    KEY_AFTER_SCHOOL_NAME = 'after_school_name'
    KEY_EDITION_CODE = 'edition_code'
    KEY_EDITION_PERIOD = 'edition_period'
    KEY_EDITION_TIMETABLE = 'edition_timetable'
    KEY_EDITION_LEVELS = 'edition_levels'
    KEY_EDITION_PRICE_FOR_MEMBERS = 'edition_price_for_members'
    KEY_EDITION_PRICE_FOR_NO_MEMBERS = 'edition_price_for_no_members'

    LABEL_AFTER_SCHOOL_NAME = _('After school name (ex. Basket)')
    LABEL_EDITION_CODE = _('Edition code')
    LABEL_EDITION_PERIOD = _('Edition period (ex. All year)')
    LABEL_EDITION_TIMETABLE = _('Edition timetable (ex. Monday/Wednesday 17-18)')
    LABEL_EDITION_LEVELS = _('Edition levels (ex. Primary)')
    LABEL_EDITION_PRICE_FOR_MEMBERS = _('Price for members')
    LABEL_EDITION_PRICE_FOR_NO_MEMBERS = _('Price for no members')

    COLUMNS_TO_IMPORT = [
        [0, FieldsFormatters.clean_string, KEY_AFTER_SCHOOL_NAME, LABEL_AFTER_SCHOOL_NAME],
        [1, FieldsFormatters.clean_string, KEY_EDITION_CODE, LABEL_EDITION_CODE],
        [2, FieldsFormatters.clean_string, KEY_EDITION_PERIOD, LABEL_EDITION_PERIOD],
        [3, FieldsFormatters.clean_string, KEY_EDITION_TIMETABLE, LABEL_EDITION_TIMETABLE],
        [4, FieldsFormatters.clean_string, KEY_EDITION_LEVELS, LABEL_EDITION_LEVELS],
        [5, FieldsFormatters.clean_integer, KEY_EDITION_PRICE_FOR_MEMBERS, LABEL_EDITION_PRICE_FOR_MEMBERS],
        [6, FieldsFormatters.clean_integer, KEY_EDITION_PRICE_FOR_NO_MEMBERS, LABEL_EDITION_PRICE_FOR_NO_MEMBERS],
    ]

    @classmethod
    def import_after_schools_activities(cls, file_content) -> Optional[List[str]]:
        logger = None
        try:
            logger = Logger(Path(__file__).stem)

            excel_importer = ExcelImporter(cls.SHEET_NUMBER,
                                           cls.FIRST_ROW_INDEX,
                                           cls.COLUMNS_TO_IMPORT,
                                           file_content=file_content)

            counters_before = cls.count_objects()

            results = []
            row: ExcelRow
            for row in excel_importer.import_rows():
                result: ImportRowResult = cls.process_row(row, logger)
                result.print(logger)
                results.append(result)

            counters_after = cls.count_objects()

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

    @classmethod
    def count_objects(cls):
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

    @classmethod
    def process_row(cls, row: ExcelRow, logger: Logger) -> ImportRowResult:
        result = ImportRowResult(row)

        if row.error:
            result.error = row.error
            return result

        try:
            after_school_result = AfterSchoolImporter.import_after_school(row.get(cls.KEY_AFTER_SCHOOL_NAME))
            result.add_partial_result(after_school_result)
            if not after_school_result.success:
                return result
            after_school = after_school_result.imported_object

            edition_result = AfterSchoolEditionImporter.import_edition(after_school,
                                                                       row.get(cls.KEY_EDITION_CODE),
                                                                       row.get(cls.KEY_EDITION_PERIOD),
                                                                       row.get(cls.KEY_EDITION_TIMETABLE),
                                                                       row.get(cls.KEY_EDITION_LEVELS),
                                                                       row.get(cls.KEY_EDITION_PRICE_FOR_MEMBERS),
                                                                       row.get(cls.KEY_EDITION_PRICE_FOR_NO_MEMBERS))
            result.add_partial_result(edition_result)

        except Exception as e:
            logger.error(f'Row {row.index + 1}: {traceback.format_exc()}')
            result.error = str(e)

        return result
