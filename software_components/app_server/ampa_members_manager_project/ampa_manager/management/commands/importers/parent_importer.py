import traceback

from ampa_manager.family.models.parent import Parent
from ampa_manager.utils.fields_formatters import FieldsFormatters
from ampa_manager.management.commands.results.import_member_result import ImportMemberResult
from ampa_manager.management.commands.imported_fields.parent_imported_fields import ParentImportedFields


class ParentImporter:

    def __init__(self, sheet, columns_indexes):
        self.sheet = sheet
        self.columns_indexes = columns_indexes

    def import_parent(self, row_index, parent_number, family):
        parent = None
        result = ImportMemberResult(Parent.__name__, row_index)

        try:
            fields = self.import_fields(row_index, parent_number)
            result.fields_excel = fields.get_list()

            if fields.name_and_surnames:
                parent, error = family.find_parent(fields.name_and_surnames)
                if parent:
                    if ParentImporter.is_modified(parent, fields.phone_number, fields.additional_phone_number, fields.email):
                        fields_before, fields_after = ParentImporter.update(parent, fields.phone_number, fields.additional_phone_number, fields.email)
                        result.set_updated(fields_before, fields_after)
                    else:
                        result.set_not_modified()
                elif error:
                    result.set_error(error)
                else:
                    fields_ok, error = ParentImporter.validate_fields(fields.name_and_surnames,
                                                                      fields.phone_number,
                                                                      fields.additional_phone_number,
                                                                      fields.email)
                    if fields_ok:
                        parent = Parent.objects.create(name_and_surnames=fields.name_and_surnames, phone_number=fields.phone_number,
                                                       additional_phone_number=fields.additional_phone_number, email=fields.email)
                        result.set_created()
                    else:
                        result.set_error(error)

                if family and not parent.belong_to_family(family):
                    family.parents.add(parent)
                    result.set_added_to_family()
            else:
                result.set_not_processed()

        except Exception as e:
            print(traceback.format_exc())
            result.set_error(f'Exception: {e}')

        return parent, result

    def import_fields(self, row_index, parent_number):
        name_and_surnames = None
        phone_number = None
        additional_phone_number = None
        email = None

        if parent_number in [1, 2]:
            name_and_surnames_index = None
            phone_number_index = None
            additional_phone_number_index = None
            email_index = None

            if parent_number == 1:
                name_and_surnames_index = self.columns_indexes['parent1_full_name']
                phone_number_index = self.columns_indexes['parent1_phone1']
                additional_phone_number_index = self.columns_indexes['parent1_phone2']
                email_index = self.columns_indexes['parent1_email']
            elif parent_number == 2:
                name_and_surnames_index = self.columns_indexes['parent2_full_name']
                phone_number_index = self.columns_indexes['parent2_phone1']
                additional_phone_number_index = self.columns_indexes['parent2_phone2']
                email_index = self.columns_indexes['parent2_email']

            name_and_surnames = FieldsFormatters.clean_name(
                self.sheet.cell_value(rowx=row_index, colx=name_and_surnames_index))
            phone_number = FieldsFormatters.clean_phone(self.sheet.cell_value(rowx=row_index, colx=phone_number_index))
            additional_phone_number = FieldsFormatters.clean_phone(
                self.sheet.cell_value(rowx=row_index, colx=additional_phone_number_index))
            email = FieldsFormatters.clean_email(self.sheet.cell_value(rowx=row_index, colx=email_index))

        return ParentImportedFields(name_and_surnames, phone_number, additional_phone_number, email)

    @staticmethod
    def is_modified(parent, phone_number, additional_phone_number, email):
        return parent.phone_number != phone_number \
               or parent.additional_phone_number != additional_phone_number \
               or parent.email != email

    @staticmethod
    def update(parent, phone_number, additional_phone_number, email):
        fields_before = [parent.name_and_surnames, parent.phone_number, parent.additional_phone_number, parent.email]
        parent.phone_number = phone_number
        parent.additional_phone_number = additional_phone_number
        parent.email = email
        parent.save()
        fields_after = [parent.name_and_surnames, parent.phone_number, parent.additional_phone_number, parent.email]
        return fields_before, fields_after

    @staticmethod
    def validate_fields(name_and_surnames, phone_number, additional_phone_number, email):
        if not name_and_surnames or type(name_and_surnames) != str:
            return False, 'Wrong name and surnames'
        return True, None
