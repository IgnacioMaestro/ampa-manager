import traceback

from ampa_members_manager.management.commands.import_command.importer import Importer
from ampa_members_manager.family.models.parent  import Parent

import ampa_members_manager.management.commands.members_excel_settings as xls_settings


class ParentImporter(Importer):

    def __init__(self, sheet):
        self.sheet = sheet

    def import_parent1(self, family, row_index):
        parent1_full_name = Importer.clean_surname(self.sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT1_FULL_NAME_INDEX))
        parent1_phone1 = Importer.clean_phone(self.sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT1_PHONE1_INDEX))
        parent1_phone2 = Importer.clean_phone(self.sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT1_PHONE2_INDEX))
        parent1_email = Importer.clean_email(self.sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT1_EMAIL_INDEX))

        return self.import_parent(parent1_full_name, parent1_phone1, parent1_phone2, parent1_email, family, row_index, 1)

    def import_parent2(self, family, row_index):
        parent2_full_name = Importer.clean_surname(self.sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT2_FULL_NAME_INDEX))
        parent2_phone1 = Importer.clean_phone(self.sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT2_PHONE1_INDEX))
        parent2_phone2 = Importer.clean_phone(self.sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT2_PHONE2_INDEX))
        parent2_email = Importer.clean_email(self.sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT2_EMAIL_INDEX))

        return self.import_parent(parent2_full_name, parent2_phone1, parent2_phone2, parent2_email, family, row_index, 2)

    def import_parent(self, full_name, phone1, phone2, email, family, row_index, parent_number):
        parent = None
        status = Importer.STATUS_NOT_PROCESSED
        added_to_family = False
        error = ''

        try:
            if full_name:
                parents = Parent.objects.by_full_name(full_name)
                if parents.count() == 1:
                    parent = parents[0]
                    if parent.phone_number != phone1 or parent.additional_phone_number != phone2 or parent.email != email:
                        parent.phone_number = phone1
                        parent.additional_phone_number = phone2
                        parent.email = email
                        parent.save()
                        status = self.set_parent_status(Importer.STATUS_UPDATED)
                    else:
                        status = self.set_parent_status(Importer.STATUS_NOT_MODIFIED)
                elif parents.count() > 1:
                    error = f'Row {row_index+1}: There is more than one parent with name "{full_name}"'
                    status = self.set_parent_status(Importer.STATUS_ERROR)
                else:
                    parent = Parent.objects.create(name_and_surnames=full_name, phone_number=phone1, additional_phone_number=phone2, email=email)
                    status = self.set_parent_status(Importer.STATUS_CREATED)
                
                if family and not parent.family_set.filter(surnames=family.surnames).exists():
                    self.set_parent_status(Importer.STATUS_UPDATED_ADDED_TO_FAMILY)
                    family.parents.add(parent)
                    added_to_family_status = True
            else:
                status = self.set_parent_status(Importer.STATUS_NOT_PROCESSED)
        except Exception as e:
            self.logger.error(traceback.format_exc())
            error = f'Row {row_index+1}: Exception processing parent {parent_number}: {e}'
            status = self.set_parent_status(Importer.STATUS_ERROR)
        finally:
            added_to_family_status = 'Added to family' if added_to_family else ''
            message = f'- Parent {parent_number}: {full_name}, {phone1}, {phone2}, {email} -> {status} {added_to_family_status} {error}'
            self.print_status(status, message)

        return parent
