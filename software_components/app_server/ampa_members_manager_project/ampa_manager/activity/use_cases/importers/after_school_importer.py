from ampa_manager.activity.models.after_school.after_school import AfterSchool
from ampa_manager.management.commands.importers.import_model_result import ImportModelResult


class AfterSchoolImporter:

    @staticmethod
    def find(name):
        try:
            return AfterSchool.objects.get(name=name)
        except AfterSchool.DoesNotExist:
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
