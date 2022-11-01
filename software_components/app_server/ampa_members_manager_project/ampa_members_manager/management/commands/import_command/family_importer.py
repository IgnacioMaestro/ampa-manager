import traceback

from ampa_members_manager.management.commands.import_command.importer import Importer
from ampa_members_manager.family.models.family import Family

import ampa_members_manager.management.commands.members_excel_settings as xls_settings


class FamilyImporter(Importer):

    def __init__(self, sheet):
        self.sheet = sheet

    def import_family(self, row_index):
        family = None
        status = Importer.STATUS_NOT_PROCESSED
        error = ''

        family_surnames = None
        family_email1 = None
        family_email2 = None

        try:
            family_surnames = Importer.clean_surname(self.sheet.cell_value(rowx=row_index, colx=xls_settings.FAMILY_SURNAMES_INDEX))
            family_email1 = Importer.clean_email(self.sheet.cell_value(rowx=row_index, colx=xls_settings.FAMILY_EMAIL1_INDEX))
            family_email2 = Importer.clean_email(self.sheet.cell_value(rowx=row_index, colx=xls_settings.FAMILY_EMAIL2_INDEX))

            if family_surnames:
                families = Family.objects.by_surnames(family_surnames)
                if families.count() == 1:
                    family = families[0]
                    if family.email != family_email1 or family.secondary_email != family_email2:
                        family.email = family_email1
                        family.secondary_email = family_email2
                        family.save()
                        status = self.set_family_status(Importer.STATUS_UPDATED)
                    else:
                        status = self.set_family_status(Importer.STATUS_NOT_MODIFIED)
                elif families.count() > 1:
                    error = f'Row {row_index+1}: There is more than one family with surnames "{family_surnames}"'
                    status = self.set_family_status(Importer.STATUS_ERROR, error)
                else:
                    family = Family.objects.create(surnames=family_surnames, email=family_email1, secondary_email=family_email2)
                    status = self.set_family_status(Importer.STATUS_CREATED)
            else:
                status = self.set_family_status(Importer.STATUS_NOT_PROCESSED)
        except Exception as e:
            self.logger.error(traceback.format_exc())
            error = f'Row {row_index+1}: Exception processing family: {e}'
            status = self.set_family_status(Importer.STATUS_ERROR, error)
        finally:
            message = f'- Family: {family_surnames}, {family_email1}, {family_email2} -> {status} {error}'
            self.print_status(status, message)

        return family
