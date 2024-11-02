from typing import Optional

from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.after_school.after_school import AfterSchool
from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult


class AfterSchoolImporter:

    def __init__(self, name: str):
        self.result = ImportModelResult(AfterSchool)
        self.name = name
        self.after_school = None

    def import_after_school(self) -> ImportModelResult:
        error_message = self.validate_fields()

        if error_message is None:
            self.after_school = AfterSchool.objects.filter(name=self.name).first()
            if self.after_school:
                self.result.set_not_modified(self.after_school)
            else:
                self.after_school = AfterSchool.objects.create(name=self.name)
                self.result.set_created(self.after_school)
        else:
            self.result.set_error(error_message)

        return self.result

    def validate_fields(self) -> Optional[str]:
        if not self.name:
            return _('Missing name')

        return None
