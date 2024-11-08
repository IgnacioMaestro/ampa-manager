from typing import Optional

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.activity.models.after_school.after_school import AfterSchool
from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.activity.use_cases.importers.after_school_activity_importer import AfterSchoolActivityImporter
from ampa_manager.activity.use_cases.importers.after_school_edition_importer import AfterSchoolEditionImporter
from ampa_manager.activity.use_cases.importers.base_importer import BaseImporter
from ampa_manager.activity.use_cases.importers.excel_column import ExcelColumn
from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult
from ampa_manager.activity.use_cases.importers.row import Row


class AfterSchoolsActivitiesImporter(BaseImporter):
    SHEET_NUMBER = 0
    FIRST_ROW_INDEX = 2

    COLUMNS_TO_IMPORT = [
        ExcelColumn(0, BaseImporter.activity_name, compulsory=True),
        ExcelColumn(1, BaseImporter.edition_code, compulsory=True),
        ExcelColumn(2, BaseImporter.edition_period, compulsory=True),
        ExcelColumn(3, BaseImporter.edition_timetable, compulsory=True),
        ExcelColumn(4, BaseImporter.edition_levels, compulsory=False),
        ExcelColumn(5, BaseImporter.edition_price_members, compulsory=True),
        ExcelColumn(6, BaseImporter.edition_price_non_members, compulsory=True),
    ]

    def process_row(self, row: Row):
        if row.any_error or row.is_empty:
            return

        try:
            activity: AfterSchool = self.import_after_school_activity(row)
            if not activity:
                return

            edition: AfterSchoolEdition = self.import_after_school_edition(row, activity)
            if not edition:
                return

        except Exception as e:
            row.error = str(e)

    @classmethod
    def import_after_school_activity(cls, row: Row) -> Optional[AfterSchool]:
        name = row.get_value(cls.KEY_ACTIVITY_NAME)
        result: ImportModelResult = AfterSchoolActivityImporter(name).import_activity()
        row.add_imported_model_result(result)
        return result.instance

    @classmethod
    def import_after_school_edition(cls, row: Row, activity: AfterSchool) -> Optional[AfterSchoolEdition]:
        active_course: AcademicCourse = ActiveCourse.load()
        code = row.get_value(cls.KEY_EDITION_CODE)
        period = row.get_value(cls.KEY_EDITION_PERIOD)
        timetable = row.get_value(cls.KEY_EDITION_TIMETABLE)
        levels = row.get_value(cls.KEY_EDITION_LEVELS)
        price_members = row.get_value(cls.KEY_EDITION_PRICE_MEMBERS)
        price_non_members = row.get_value(cls.KEY_EDITION_PRICE_NON_MEMBERS)

        result: ImportModelResult = AfterSchoolEditionImporter(
            activity, active_course, code, period, timetable, levels, price_members, price_non_members).import_edition()

        row.add_imported_model_result(result)

        return result.instance
