from typing import Optional

from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.camps.camps_edition import CampsEdition
from ampa_manager.activity.models.camps.camps_registration import CampsRegistration
from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.holder.holder import Holder


class CampsRegistrationImporter:

    def __init__(self, edition: CampsEdition, holder: Holder, child: Child):
        self.result = ImportModelResult(CampsRegistration)
        self.edition = edition
        self.holder = holder
        self.child = child
        self.registration = None

    def import_registration(self) -> ImportModelResult:
        error_message = self.validate_fields()
        if error_message is None:
            self.registration = self.find_registration()
            if self.registration:
                self.result.set_not_modified(self.registration)
            else:
                self.manage_not_found_registration()
        else:
            self.result.set_error(error_message)

        return self.result

    def find_registration(self) -> Optional[CampsRegistration]:
        try:
            return CampsRegistration.objects.get(custody_edition=self.edition, child=self.child)
        except CampsRegistration.DoesNotExist:
            return None

    def manage_not_found_registration(self):
        registration = CampsRegistration.objects.create(
            custody_edition=self.edition, holder=self.holder, child=self.child)
        self.result.set_created(registration)

    def validate_fields(self) -> Optional[str]:
        if not self.edition:
            return _('Missing edition')

        if not self.holder:
            return _('Missing holder')

        if not self.child:
            return _('Missing child')

        return None
