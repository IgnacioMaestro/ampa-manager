from typing import Optional

from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult, ModifiedField
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.holder.holder import Holder


class CustodyRegistrationImporter:

    def __init__(self, edition: CustodyEdition, holder: Holder, child: Child, assisted_days: int):
        self.result = ImportModelResult(CustodyRegistration)
        self.edition = edition
        self.holder = holder
        self.child = child
        self.assisted_days = assisted_days
        self.registration = None

    def import_registration(self) -> ImportModelResult:
        error_message = self.validate_fields()
        if error_message is None:
            self.registration = self.find_registration()
            if self.registration:
                self.manage_found_registration()
            else:
                self.manage_not_found_registration()
        else:
            self.result.set_error(error_message)

        return self.result

    def find_registration(self) -> Optional[CustodyRegistration]:
        try:
            return CustodyRegistration.objects.get(custody_edition=self.edition, child=self.child)
        except CustodyRegistration.DoesNotExist:
            return None

    def manage_not_found_registration(self):
        if self.assisted_days > 0:
            registration = CustodyRegistration.objects.create(
                custody_edition=self.edition, holder=self.holder, child=self.child,
                assisted_days=self.assisted_days)
            self.result.set_created(registration)
        else:
            self.result.set_omitted(self.registration, _('0 assisted days'))

    def manage_found_registration(self):
        if self.registration_is_modified():
            modified_fields = []

            if self.registration.holder != self.holder:
                modified_fields.append(ModifiedField(_('Holder'), self.registration.holder, self.holder))
                self.registration.holder = self.holder

            if self.registration.assisted_days != self.assisted_days:
                modified_fields.append(
                    ModifiedField(_('Assisted days'), self.registration.assisted_days, self.assisted_days))
                self.registration.assisted_days = self.assisted_days

            self.registration.save()

            self.result.set_updated(self.registration, modified_fields)
        else:
            self.result.set_not_modified(self.registration)

    def registration_is_modified(self):
        return self.registration.holder != self.holder or self.registration.assisted_days != self.assisted_days

    def validate_fields(self) -> Optional[str]:
        if not self.edition:
            return _('Missing edition')

        if not self.holder:
            return _('Missing holder')

        if not self.child:
            return _('Missing child')

        if self.assisted_days is None or not isinstance(self.assisted_days, int) or self.assisted_days <= 0:
            assisted_days = self.assisted_days if self.assisted_days else '-'
            return _('Wrong assisted days') + f': ({assisted_days})'

        return None
