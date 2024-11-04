from typing import Optional

from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult, ModifiedField
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.holder.holder import Holder


class AfterSchoolRegistrationImporter:

    def __init__(self, edition: AfterSchoolEdition, holder: Holder, child: Child):
        self.result = ImportModelResult(AfterSchoolRegistration)
        self.edition = edition
        self.holder = holder
        self.child = child
        self.registration = None

    def import_registration(self) -> ImportModelResult:
        try:
            error_message = self.validate_fields()

            if error_message is None:
                self.registration = self.find_registration()
                if self.registration:
                    self.manage_found_registration()
                else:
                    self.manage_not_found_registration()
            else:
                self.result.set_error(error_message)
        except Exception as e:
            self.result.set_error(str(e))

        return self.result

    def find_registration(self) -> Optional[AfterSchoolRegistration]:
        return AfterSchoolRegistration.objects.filter(
            after_school_edition=self.edition, child=self.child).first()

    def manage_not_found_registration(self):
        self.registration = AfterSchoolRegistration.objects.create(
            after_school_edition=self.edition, child=self.child, holder=self.holder)
        self.result.set_created(self.registration)

    def manage_found_registration(self):
        if self.registration.holder != self.holder:
            modified_fields = [ModifiedField(_('Holder'), self.registration.holder, self.holder)]
            self.registration.holder = self.holder
            self.result.set_updated(self.registration, modified_fields)
        else:
            self.result.set_not_modified(self.registration)

    def validate_fields(self) -> Optional[str]:
        if not self.edition:
            return _('Missing after school edition')

        if not self.holder:
            return _('Missing holder')

        if not self.child:
            return _('Missing child')

        return None
