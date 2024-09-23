from typing import Optional

from ampa_manager.family.models.parent import Parent
from ampa_manager.activity.use_cases.importers.fields_changes import FieldsChanges
from ampa_manager.utils.excel.import_model_result import ImportModelResult


class ParentImporter:

    def __init__(self, family, name_and_surnames: str, phone_number: str, additional_phone_number: Optional[str],
                 email: str):
        self.result = ImportModelResult(Parent.__name__)
        self.family = family
        self.name_and_surnames = name_and_surnames
        self.phone_number = phone_number
        self.additional_phone_number = additional_phone_number
        self.email = email
        self.parent = None

    def import_parent(self) -> ImportModelResult:
        error_message = self.validate_fields()

        if name_and_surnames or phone_number or additional_phone_number or email:
            fields_ok, error = ParentImporter.validate_fields(family,
                                                              name_and_surnames,
                                                              phone_number,
                                                              additional_phone_number,
                                                              email)
            if fields_ok:
                parent = family.find_parent(name_and_surnames)
                if parent:
                    if parent.is_modified(phone_number, additional_phone_number, email):
                        fields_changes: FieldsChanges = parent.update(phone_number, additional_phone_number, email, allow_reset=False)
                        result.set_updated(parent, fields_changes)
                    else:
                        result.set_not_modified(parent)
                else:
                    parent = Parent.objects.create(name_and_surnames=name_and_surnames,
                                                   phone_number=phone_number,
                                                   additional_phone_number=additional_phone_number,
                                                   email=email)
                    result.set_created(parent)

                    family.parents.add(parent)
                    result.set_parent_added_to_family()
            else:
                result.set_error(error)
        elif optional:
            result.set_omitted('No data')
        else:
            result.set_error('Missing all data')

        return result

    def validate_fields(self) -> Optional[str]:
        if not self.family:
            return _('Missing family')

        if not self.name_and_surnames or not isinstance(self.name_and_surnames, str):
            return _('Missing/Wrong name and surnames') + f' ({self.name_and_surnames})'

        if self.phone_number and type(self.phone_number) != str:
            return False, f'Missing/Wrong phone number: {self.phone_number} ({type(self.phone_number)})'
        if self.additional_phone_number and type(self.additional_phone_number) != str:
            return False, f'Missing/Wrong additional phone number: {self.additional_phone_number} ({type(self.additional_phone_number)})'
        if self.email and type(self.email) != str:
            return False, f'Missing/Wrong email: {self.email} ({type(self.email)})'
        return True, None
