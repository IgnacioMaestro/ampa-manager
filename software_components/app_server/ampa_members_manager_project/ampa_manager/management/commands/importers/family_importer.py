import traceback

from ampa_manager.family.models.family import Family
from ampa_manager.utils.fields_formatters import FieldsFormatters
from ampa_manager.management.commands.results.import_member_result import ImportMemberResult


class FamilyImporter:

    def __init__(self, sheet, columns_indexes):
        self.sheet = sheet
        self.columns_indexes = columns_indexes

    def import_family(self, row_index):
        family = None
        result = ImportMemberResult(Family.__name__, row_index)

        try:
            surnames, parent1_fullname, parent2_fullname = self.import_fields(row_index)
            result.fields_excel = [surnames]

            if surnames:
                family, error = Family.find(surnames, [parent1_fullname, parent2_fullname])
                if family:
                    if FamilyImporter.is_modified(family):
                        fields_before, fields_after = FamilyImporter.update(family)
                        result.set_updated(fields_before, fields_after)
                    else:
                        result.set_not_modified()
                elif error:
                    result.set_error(error)
                else:
                    family = Family.objects.create(surnames=surnames)
                    result.set_created()
            else:
                result.set_not_processed()

        except Exception as e:
            print(traceback.format_exc())
            result.set_error(f'Exception: {e}')

        return family, result

    def import_fields(self, row_index):
        surnames = FieldsFormatters.clean_name(self.sheet.cell_value(rowx=row_index, colx=self.columns_indexes['family_surnames']))
        parent1_fullname = FieldsFormatters.clean_name(self.sheet.cell_value(rowx=row_index, colx=self.columns_indexes['parent1_full_name']))
        parent2_fullname = FieldsFormatters.clean_name(self.sheet.cell_value(rowx=row_index, colx=self.columns_indexes['parent2_full_name']))
        return surnames, parent1_fullname, parent2_fullname

    @staticmethod
    def is_modified(family):
        return family.decline_membership

    @staticmethod
    def update(family):
        fields_before = [family.decline_membership]
        family.decline_membership = False
        family.save()
        fields_after = [family.decline_membership]
        return fields_before, fields_after
