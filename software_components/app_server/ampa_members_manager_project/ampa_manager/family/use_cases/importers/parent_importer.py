from ampa_manager.family.models.parent import Parent
from ampa_manager.management.commands.results.model_import_result import ModelImportResult


class ParentImporter:

    @staticmethod
    def import_parent(family, name_and_surnames: str, phone_number: str, additional_phone_number: str, email:str) -> ModelImportResult:
        result = ModelImportResult(Parent.__name__, [name_and_surnames, phone_number, additional_phone_number, email])

        fields_ok, error = ParentImporter.validate_fields(name_and_surnames,
                                                          phone_number,
                                                          additional_phone_number,
                                                          email)
        if fields_ok:
            parent = family.find_parent(name_and_surnames)
            if parent:
                if parent.is_modified(phone_number, additional_phone_number, email):
                    fields_before, fields_after = parent.update(phone_number, additional_phone_number, email)
                    result.set_updated(parent, fields_before, fields_after)
                else:
                    result.set_not_modified(parent)
            else:
                parent = Parent.objects.create(name_and_surnames=name_and_surnames,
                                               phone_number=phone_number,
                                               additional_phone_number=additional_phone_number,
                                               email=email)
                result.set_created(parent)

                family.parents.add(parent)
                result.set_added_to_family()
        else:
            result.set_error(error)

        return result

    @staticmethod
    def validate_fields(name_and_surnames, phone_number, additional_phone_number, email):
        if not name_and_surnames or type(name_and_surnames) != str:
            return False, f'Wrong name and surnames: {name_and_surnames} ({type(name_and_surnames)})'
        if phone_number and type(phone_number) != str:
            return False, f'Wrong phone number: {phone_number} ({type(phone_number)})'
        if additional_phone_number and type(additional_phone_number) != str:
            return False, f'Wrong additional phone number: {additional_phone_number} ({type(additional_phone_number)})'
        if email and type(email) != str:
            return False, f'Wrong email: {email} ({type(email)})'
        return True, None