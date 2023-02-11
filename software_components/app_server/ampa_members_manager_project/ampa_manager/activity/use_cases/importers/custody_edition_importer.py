from typing import Optional

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.activity.models.after_school.after_school import AfterSchool
from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.management.commands.importers.import_model_result import ImportModelResult
from ampa_manager.utils.string_utils import StringUtils


class CustodyEditionImporter:

    @staticmethod
    def find(academic_course: AcademicCourse, period: str, cycle: str) -> Optional[CustodyEdition]:
        for custody_edition in CustodyEdition.objects.filter(academic_course=academic_course, cycle=cycle):
            if StringUtils.compare_ignoring_everything(custody_edition.period, period):
                return custody_edition
        return None

    @staticmethod
    def import_custody_edition(academic_course: AcademicCourse, period: str, cycle: str) -> ImportModelResult:
        result = ImportModelResult(CustodyEdition.__name__, [academic_course, period, cycle])

        custody_edition = CustodyEditionImporter.find(academic_course, period, cycle)
        if custody_edition:
            result.set_not_modified(custody_edition)
        else:
            result.set_error(f'Not found: "{academic_course}", "{period}", "{cycle}"')

        return result
