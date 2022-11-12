import traceback

from ampa_members_manager.management.commands.import_command.importer import Importer
from ampa_members_manager.family.models.family import Family
from ampa_members_manager.management.commands.import_command.processing_result import ProcessingResult


class FamilyImporter(Importer):

    def __init__(self, sheet, xls_settings):
        self.sheet = sheet
        self.xls_settings = xls_settings

    def import_family(self, row_index):
        family = None
        result = ProcessingResult(Family.__name__, row_index)

        try:
            surnames = Importer.clean_surname(self.sheet.cell_value(rowx=row_index, colx=self.xls_settings.FAMILY_SURNAMES_INDEX))

            result.fields_excel = [surnames]

            if surnames:
                families = Family.objects.by_surnames(surnames)
                if families.count() == 1:
                    family = families[0]
                    result.set_not_modified()
                elif families.count() > 1:
                    result.set_error('There is more than one family with surnames "{surnames}"')
                else:
                    family = Family.objects.create(surnames=surnames)
                    result.set_created()
            else:
                result.set_not_processed()

        except Exception as e:
            print(traceback.format_exc())
            result.set_error(f'Exception: {e}')

        return family, result
