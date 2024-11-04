from typing import Optional

from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult, ModifiedField
from ampa_manager.family.models.parent import Parent


class ParentImporter:

    def __init__(self, family, name_and_surnames: str, phone_number: str, additional_phone_number: Optional[str],
                 email: str, compulsory: bool):
        self.result = ImportModelResult(Parent)
        self.family = family
        self.name_and_surnames = name_and_surnames
        self.phone_number = phone_number
        self.additional_phone_number = additional_phone_number
        self.email = email
        self.compulsory = compulsory
        self.parent = None

    def import_parent(self) -> ImportModelResult:
        try:
            if not self.compulsory and self.all_parent_fields_are_empty():
                self.result.set_omitted()
                return self.result

            error_message = self.validate_fields()

            if error_message is None:
                self.parent = self.find_parent()
                if self.parent:
                    self.manage_found_parent()
                else:
                    self.manage_not_found_parent()
            else:
                self.result.set_error(error_message)
        except Exception as e:
            self.result.set_error(str(e))

        return self.result

    def find_parent(self) -> Optional[Parent]:
        family_parents = self.family.parents.all()
        for parent in family_parents:
            if parent.matches_name_and_surnames(self.name_and_surnames, strict=True):
                return parent
        for parent in family_parents:
            if parent.matches_name_and_surnames(self.name_and_surnames, strict=False):
                return parent
        return None

    def all_parent_fields_are_empty(self):
        return not self.name_and_surnames and not self.phone_number and not self.additional_phone_number and not self.email

    def manage_not_found_parent(self):
        self.parent = Parent.objects.create(
            name_and_surnames=self.name_and_surnames, phone_number=self.phone_number,
            additional_phone_number=self.additional_phone_number, email=self.email)
        self.result.set_created(self.parent)
        self.family.parents.add(self.parent)

    def manage_found_parent(self):
        if self.parent_is_modified():
            modified_fields = []

            if self.phone_number is not None and self.phone_number != self.parent.phone_number:
                modified_fields.append(ModifiedField(_('Phone number'), self.parent.phone_number, self.phone_number))
                self.parent.phone_number = self.phone_number

            if self.additional_phone_number is not None and self.additional_phone_number != self.parent.additional_phone_number:
                modified_fields.append(ModifiedField(_('Additional phone number'), self.parent.additional_phone_number, self.additional_phone_number))
                self.parent.additional_phone_number = self.additional_phone_number

            if self.email is not None and self.email != self.parent.email:
                modified_fields.append(ModifiedField(_('Email'), self.parent.email, self.email))
                self.parent.email = self.email

            self.result.set_updated(self.parent, modified_fields)
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
        return ((self.phone_number is not None and self.phone_number != self.parent.phone_number) or
                (self.additional_phone_number is not None and self.additional_phone_number != self.parent.additional_phone_number) or
                (self.email is not None and self.email != self.parent.email))
