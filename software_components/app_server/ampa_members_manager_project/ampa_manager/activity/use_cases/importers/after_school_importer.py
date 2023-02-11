from typing import Optional

from ampa_manager.activity.models.after_school.after_school import AfterSchool
from ampa_manager.management.commands.importers.import_model_result import ImportModelResult
from ampa_manager.utils.string_utils import StringUtils


class AfterSchoolImporter:

    @staticmethod
    def find(name) -> Optional[AfterSchool]:
        for after_school in AfterSchool.objects.all():
            if StringUtils.compare_ignoring_everything(after_school.name, name):
                return after_school
        return None

    @staticmethod
    def import_after_school(name) -> ImportModelResult:
        result = ImportModelResult(AfterSchool.__name__, [name])

        after_school = AfterSchoolImporter.find(name)
        if after_school:
            result.set_not_modified(after_school)
        else:
            result.set_error(f'Not found: "{name}"')

        return result
