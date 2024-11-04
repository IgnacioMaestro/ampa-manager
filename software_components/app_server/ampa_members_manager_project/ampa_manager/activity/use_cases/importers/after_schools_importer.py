from typing import Optional

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.activity.models.after_school.after_school import AfterSchool
from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.activity.use_cases.importers.after_school_activity_importer import AfterSchoolActivityImporter
from ampa_manager.activity.use_cases.importers.after_school_edition_importer import AfterSchoolEditionImporter
from ampa_manager.activity.use_cases.importers.after_school_registration_importer import AfterSchoolRegistrationImporter
from ampa_manager.activity.use_cases.importers.base_importer import BaseImporter
from ampa_manager.activity.use_cases.importers.excel_column import ExcelColumn
from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult
from ampa_manager.activity.use_cases.importers.row import Row
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.parent import Parent
from ampa_manager.family.use_cases.importers.family_holders_consolidator import FamilyHoldersConsolidator


class AfterSchoolsImporter(BaseImporter):
    SHEET_NUMBER = 0
    FIRST_ROW_INDEX = 2

    COLUMNS_TO_IMPORT = [
        ExcelColumn(0, BaseImporter.family_email, compulsory=True),
        ExcelColumn(1, BaseImporter.parent_1_name_and_surnames, compulsory=False),
        ExcelColumn(2, BaseImporter.parent_1_phone_number, compulsory=False),
        ExcelColumn(3, BaseImporter.parent_1_email, compulsory=False),
        ExcelColumn(4, BaseImporter.bank_account_iban, compulsory=False),
        ExcelColumn(5, BaseImporter.child_1_name, compulsory=True),
        ExcelColumn(6, BaseImporter.family_surnames, compulsory=False),
        ExcelColumn(7, BaseImporter.child_1_year_of_birth, compulsory=False),
        ExcelColumn(8, BaseImporter.child_1_level, compulsory=False),
        ExcelColumn(9, BaseImporter.activity_name, compulsory=True),
        ExcelColumn(10, BaseImporter.activity_period, compulsory=False),
        ExcelColumn(11, BaseImporter.activity_timetable, compulsory=False),
        ExcelColumn(12, BaseImporter.activity_price_members, compulsory=False),
        ExcelColumn(13, BaseImporter.activity_price_non_members, compulsory=False),
    ]

    def process_row(self, row: Row):
        if row.any_error or row.is_empty:
            return

        try:
            family: Family = self.import_family(row)
            if not family:
                return

            child: Child = self.import_child(row, family, compulsory=True)
            if not child:
                return

            parent: Parent = self.import_parent(row, family, compulsory=True)
            if not parent:
                return

            holder: Optional[Holder] = self.import_bank_account_and_holder(row, parent)
            if holder:
                family.update_membership_holder(holder)

            FamilyHoldersConsolidator(family).consolidate()

            if not family.after_school_holder:
                row.set_error('Missing bank account')
                return

            activity: AfterSchool = self.import_after_school_activity(row)
            if not activity:
                return

            edition: AfterSchoolEdition = self.import_after_school_edition(row, activity)
            if not edition:
                return

            self.import_after_school_registration(row, edition, family.after_school_holder, child)

        except Exception as e:
            row.error = str(e)

    @classmethod
    def import_after_school_activity(cls, row: Row) -> Optional[AfterSchool]:
        name = row.get_value(cls.KEY_ACTIVITY_NAME)
        result: ImportModelResult = AfterSchoolActivityImporter(name).import_activity()
        row.add_imported_model_result(result)
        return result.instance

    @classmethod
    def import_after_school_edition(cls, row: Row, after_school: AfterSchool) -> Optional[AfterSchoolEdition]:
        active_course: AcademicCourse = ActiveCourse.load()
        period = row.get_value(cls.KEY_ACTIVITY_PERIOD)
        timetable = row.get_value(cls.KEY_ACTIVITY_TIMETABLE)
        price_members = row.get_value(cls.KEY_ACTIVITY_PRICE_MEMBERS)
        price_non_members = row.get_value(cls.KEY_ACTIVITY_PRICE_NON_MEMBERS)

        result: ImportModelResult = AfterSchoolEditionImporter(
            after_school, active_course, period, timetable, price_members, price_non_members).import_edition()

        row.add_imported_model_result(result)

        return result.instance

    @classmethod
    def import_after_school_registration(
            cls, row: Row, edition: AfterSchoolEdition, holder: Holder, child: Child) -> AfterSchoolRegistration:

        result: ImportModelResult = AfterSchoolRegistrationImporter(edition, holder, child).import_registration()
        row.add_imported_model_result(result)

        return result.instance
