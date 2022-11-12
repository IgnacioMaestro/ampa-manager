import traceback

from ampa_members_manager.management.commands.import_command.importer import Importer
from ampa_members_manager.family.models.parent  import Parent
from ampa_members_manager.management.commands.import_command.processing_result import ProcessingResult


class ParentImporter(Importer):

    def __init__(self, sheet, xls_settings):
        self.sheet = sheet
        self.xls_settings = xls_settings

    def get_fields(self, row_index, parent_number):
        if parent_number in [1, 2]:
            if parent_number == 1:
                name_and_surnames_index = self.xls_settings.PARENT1_FULL_NAME_INDEX
                phone1_index = self.xls_settings.PARENT1_PHONE1_INDEX
                phone2_index = self.xls_settings.PARENT1_PHONE2_INDEX
                email_index = self.xls_settings.PARENT1_EMAIL_INDEX
            elif parent_number == 2:
                name_and_surnames_index = self.xls_settings.PARENT2_FULL_NAME_INDEX
                phone1_index = self.xls_settings.PARENT2_PHONE1_INDEX
                phone2_index = self.xls_settings.PARENT2_PHONE2_INDEX
                email_index = self.xls_settings.PARENT2_EMAIL_INDEX
            
            name_and_surnames = Importer.clean_surname(self.sheet.cell_value(rowx=row_index, colx=name_and_surnames_index))
            phone1 = Importer.clean_phone(self.sheet.cell_value(rowx=row_index, colx=phone1_index))
            phone2 = Importer.clean_phone(self.sheet.cell_value(rowx=row_index, colx=phone2_index))
            email = Importer.clean_email(self.sheet.cell_value(rowx=row_index, colx=email_index))

            return name_and_surnames, phone1, phone2, email
        return None, None, None, None

    def import_parent(self, row_index, parent_number, family):
        parent = None
        result = ProcessingResult(Parent.__name__, row_index)

        try:

            name_and_surnames, phone1, phone2, email = self.get_fields(row_index, parent_number)
            result.fields_excel = [name_and_surnames, phone1, phone2, email]

            if name_and_surnames:
                parents = Parent.objects.by_full_name(name_and_surnames)
                if parents.count() == 1:
                    parent = parents[0]
                    if parent.phone_number != phone1 or parent.additional_phone_number != phone2 or parent.email != email:
                        fields_before = [parent.name_and_surnames, parent.phone_number, parent.additional_phone_number, parent.email]
                        parent.phone_number = phone1
                        parent.additional_phone_number = phone2
                        parent.email = email
                        parent.save()
                        fields_after = [parent.name_and_surnames, parent.phone_number, parent.additional_phone_number, parent.email]
                        result.set_updated(fields_before, fields_after)
                    else:
                        result.set_not_modified()
                elif parents.count() > 1:
                    result.set_error('There is more than one parent with name "{name_and_surnames}"')
                else:
                    parent = Parent.objects.create(name_and_surnames=name_and_surnames, phone_number=phone1, additional_phone_number=phone2, email=email)
                    result.set_created()
                
                if family and not parent.belong_to_family(family):
                    family.parents.add(parent)
                    result.set_added_to_family()

            else:
                result.set_not_processed()

        except Exception as e:
            print(traceback.format_exc())
            result.set_error(f'Exception: {e}')

        return parent, result
