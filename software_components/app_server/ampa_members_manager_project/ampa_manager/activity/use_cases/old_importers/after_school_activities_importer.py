from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.after_school.after_school import AfterSchool
from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.activity.use_cases.old_importers.after_school_edition_importer import AfterSchoolEditionImporter
from ampa_manager.activity.use_cases.old_importers.after_school_importer import AfterSchoolImporter
from ampa_manager.activity.use_cases.old_importers.excel.excel_importer import ExcelImporter
from ampa_manager.activity.use_cases.old_importers.excel.excel_row import ExcelRow
from ampa_manager.activity.use_cases.old_importers.excel.import_row_result import ImportRowResult
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.parent import Parent
from ampa_manager.utils.fields_formatters import FieldsFormatters
from ampa_manager.views.import_info import ImportInfo


class AfterSchoolsActivitiesImporter:
    SHEET_NUMBER = 0
    FIRST_ROW_INDEX = 2

    KEY_AFTER_SCHOOL_NAME = 'after_school_name'
    KEY_EDITION_PERIOD = 'edition_period'
    KEY_EDITION_TIMETABLE = 'edition_timetable'
    KEY_EDITION_LEVELS = 'edition_levels'
    KEY_EDITION_PRICE_FOR_MEMBERS = 'edition_price_for_members'
    KEY_EDITION_PRICE_FOR_NO_MEMBERS = 'edition_price_for_no_members'

    LABEL_AFTER_SCHOOL_NAME = _('After school name (ex. Basket)')
    LABEL_EDITION_PERIOD = _('Edition period (ex. All year)')
    LABEL_EDITION_TIMETABLE = _('Edition timetable (ex. Monday/Wednesday 17-18)')
    LABEL_EDITION_LEVELS = _('Edition levels (ex. Primary)')
    LABEL_EDITION_PRICE_FOR_MEMBERS = _('Price for members')
    LABEL_EDITION_PRICE_FOR_NO_MEMBERS = _('Price for no members')

    COLUMNS_TO_IMPORT = [
        [0, FieldsFormatters.format_string, KEY_AFTER_SCHOOL_NAME, LABEL_AFTER_SCHOOL_NAME],
        [1, FieldsFormatters.format_string, KEY_EDITION_PERIOD, LABEL_EDITION_PERIOD],
        [2, FieldsFormatters.format_string, KEY_EDITION_TIMETABLE, LABEL_EDITION_TIMETABLE],
        [3, FieldsFormatters.format_string, KEY_EDITION_LEVELS, LABEL_EDITION_LEVELS],
        [4, FieldsFormatters.format_integer, KEY_EDITION_PRICE_FOR_MEMBERS, LABEL_EDITION_PRICE_FOR_MEMBERS],
        [5, FieldsFormatters.format_integer, KEY_EDITION_PRICE_FOR_NO_MEMBERS, LABEL_EDITION_PRICE_FOR_NO_MEMBERS],
    ]

    @classmethod
    def import_activities(cls, file_content) -> ImportInfo:
        importer = ExcelImporter(
            cls.SHEET_NUMBER, cls.FIRST_ROW_INDEX, cls.COLUMNS_TO_IMPORT, file_content=file_content)

        importer.counters_before = cls.count_objects()

        for row in importer.get_rows():
            result = cls.process_row(row)
            importer.add_result(result)

        importer.counters_after = cls.count_objects()

        return ImportInfo(
            importer.total_rows, importer.successfully_imported_rows, importer.get_summary(), importer.get_results())

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
    def process_row(cls, row: ExcelRow) -> ImportRowResult:
        result = ImportRowResult(row)

        if row.error:
            result.error = row.error
            return result

        try:
            after_school_result = AfterSchoolImporter.import_after_school(row.get(cls.KEY_AFTER_SCHOOL_NAME), True)
            result.add_partial_result(after_school_result)
            if not after_school_result.success:
                return result
            after_school = after_school_result.imported_object

            edition_result = AfterSchoolEditionImporter.import_edition(
                after_school,
                row.get(cls.KEY_EDITION_PERIOD),
                row.get(cls.KEY_EDITION_TIMETABLE),
                row.get(cls.KEY_EDITION_LEVELS),
                row.get(cls.KEY_EDITION_PRICE_FOR_MEMBERS),
                row.get(cls.KEY_EDITION_PRICE_FOR_NO_MEMBERS))
            result.add_partial_result(edition_result)

        except Exception as e:
            result.error = str(e)

        return result
