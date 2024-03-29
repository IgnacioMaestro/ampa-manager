from typing import Optional

from ampa_manager.family.models.parent import Parent
from ampa_manager.family.use_cases.importers.fields_changes import FieldsChanges
from ampa_manager.utils.excel.import_model_result import ImportModelResult


class ParentImporter:

    @staticmethod
    def import_parent(family, name_and_surnames: str, phone_number: str, additional_phone_number: Optional[str],
                      email: str, optional=False) -> ImportModelResult:
        result = ImportModelResult(Parent.__name__, [name_and_surnames, phone_number, additional_phone_number, email])

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

    @staticmethod
    def validate_fields(family, name_and_surnames, phone_number, additional_phone_number, email):
        if not family:
            return False, f'Missing family'
        if not name_and_surnames or type(name_and_surnames) != str:
            return False, f'Missing/Wrong name and surnames: {name_and_surnames} ({type(name_and_surnames)})'
        if phone_number and type(phone_number) != str:
            return False, f'Missing/Wrong phone number: {phone_number} ({type(phone_number)})'
        if additional_phone_number and type(additional_phone_number) != str:
            return False, f'Missing/Wrong additional phone number: {additional_phone_number} ({type(additional_phone_number)})'
        if email and type(email) != str:
            return False, f'Missing/Wrong email: {email} ({type(email)})'
        return True, None
