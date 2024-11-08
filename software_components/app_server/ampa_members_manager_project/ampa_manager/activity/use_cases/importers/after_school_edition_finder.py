from typing import Optional

from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult


class AfterSchoolEditionFinder:

    def __init__(self, code: str):
        self.result = ImportModelResult(AfterSchoolEdition)
        self.code = code
        self.edition = None

    def find_edition(self) -> ImportModelResult:
        try:
            error_message = self.validate_fields()
            if error_message is None:
                try:
                    self.edition = AfterSchoolEdition.objects.get(code=self.code)
                    self.result.set_not_modified(self.edition)
                except AfterSchoolEdition.DoesNotExist:
                    self.result.set_error(_('Edition not found'))
            else:
                self.result.set_error(error_message)
        except Exception as e:
            self.result.set_error(str(e))

        return self.result


    def validate_fields(self) -> Optional[str]:
        if not self.code:
            return _('Missing code')
