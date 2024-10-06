from typing import Optional

from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult
from ampa_manager.family.models.parent import Parent


class ParentImporter:

    def __init__(self, family, name_and_surnames: str, phone_number: str, additional_phone_number: Optional[str],
                 email: str):
        self.result = ImportModelResult(Parent)
        self.family = family
        self.name_and_surnames = name_and_surnames
        self.phone_number = phone_number
        self.additional_phone_number = additional_phone_number
        self.email = email
        self.parent = None

    def import_parent(self) -> ImportModelResult:
        error_message = self.validate_fields()

        if error_message is None:
            self.parent = self.family.find_parent(self.name_and_surnames)
            if self.parent:
                self.manage_found_parent()
            else:
                self.manage_not_found_parent()
        else:
            self.result.set_error(error_message)

        return self.result

    def manage_not_found_parent(self):
        parent = Parent.objects.create(name_and_surnames=self.name_and_surnames,
                                       phone_number=self.phone_number,
                                       additional_phone_number=self.additional_phone_number,
                                       email=self.email)
        self.result.set_created(parent)
        self.family.parents.add(parent)

    def manage_found_parent(self):
        if self.parent_is_modified():
            values_before = [self.parent.phone_number, self.parent.additional_phone_number, self.parent.email]

            if self.phone_number is not None:
                self.parent.phone_number = self.phone_number

            if self.additional_phone_number is not None:
                self.parent.additional_phone_number = self.additional_phone_number

            if self.email is not None:
                self.parent.email = self.email

            values_after = [self.parent.phone_number, self.parent.additional_phone_number, self.parent.email]

            self.result.set_updated(self.parent, values_before, values_after)
        else:
            self.result.set_not_modified(self.parent)

    def validate_fields(self) -> Optional[str]:
        if not self.family:
            return _('Missing family')

        if not self.name_and_surnames or not isinstance(self.name_and_surnames, str):
            return _('Missing/Wrong name and surnames') + f' ({self.name_and_surnames})'

        if self.phone_number and not isinstance(self.phone_number, str):
            return _('Missing/Wrong phone number') + f' ({self.phone_number})'

        if self.additional_phone_number and not isinstance(self.additional_phone_number, str):
            return _('Missing/Wrong additional phone number') + f' ({self.additional_phone_number})'

        if self.email and not isinstance(self.email, str):
            return _('Missing/Wrong email') + f' ({self.email})'

        return None

    def parent_is_modified(self):
        return ((self.phone_number and self.phone_number != self.parent.phone_number) or
                (self.additional_phone_number and self.additional_phone_number != self.parent.additional_phone_number) or
                (self.email and not self.email != self.parent.email))
