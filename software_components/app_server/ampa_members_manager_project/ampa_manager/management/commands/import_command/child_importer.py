import traceback

from ampa_manager.management.commands.import_command.importer import Importer
from ampa_manager.family.models.child import Child
from ampa_manager.management.commands.import_command.processing_result import ProcessingResult
from ampa_manager.academic_course.models.level import Level


class ChildImporter(Importer):

    def __init__(self, sheet, xls_settings):
        self.sheet = sheet
        self.xls_settings = xls_settings

    def get_fields(self, row_index, child_number):
        if child_number in [1, 2, 3, 4, 5]:
            if child_number == 1:
                name_index = self.xls_settings.CHILD1_NAME_INDEX
                year_index = self.xls_settings.CHILD1_YEAR_INDEX
                level_index = self.xls_settings.CHILD1_LEVEL_INDEX
            elif child_number == 2:
                name_index = self.xls_settings.CHILD2_NAME_INDEX
                year_index = self.xls_settings.CHILD2_YEAR_INDEX
                level_index = self.xls_settings.CHILD2_LEVEL_INDEX
            elif child_number == 3:
                name_index = self.xls_settings.CHILD3_NAME_INDEX
                year_index = self.xls_settings.CHILD3_YEAR_INDEX
                level_index = self.xls_settings.CHILD3_LEVEL_INDEX
            elif child_number == 4:
                name_index = self.xls_settings.CHILD4_NAME_INDEX
                year_index = self.xls_settings.CHILD4_YEAR_INDEX
                level_index = self.xls_settings.CHILD4_LEVEL_INDEX
            elif child_number == 5:
                name_index = self.xls_settings.CHILD5_NAME_INDEX
                year_index = self.xls_settings.CHILD5_YEAR_INDEX
                level_index = self.xls_settings.CHILD5_LEVEL_INDEX
            
            name = Importer.clean_surname(self.sheet.cell_value(rowx=row_index, colx=name_index))
            year = Importer.clean_integer(self.sheet.cell_value(rowx=row_index, colx=year_index))
            level = Level.parse_level(self.sheet.cell_value(rowx=row_index, colx=level_index))

            return name, year, level
        return None, None, None

    def import_child(self, row_index, child_number, family):
        child = None
        result = ProcessingResult(Child.__name__, row_index)

        try:
            name, year_of_birth, level = self.get_fields(row_index, child_number)
            result.fields_excel = [name, year_of_birth, level]

            if name and family:
                repetition = Level.calculate_repetition(level, year_of_birth)

                children = Child.objects.with_name_and_of_family(name, family)
                if children.count() == 1:
                    child = children[0]
                    if child.year_of_birth != year_of_birth or child.repetition != repetition:
                        fields_before = [child.name, child.year_of_birth, child.level, child.repetition]
                        child.year_of_birth = year_of_birth
                        child.repetition = repetition
                        child.save()
                        fields_after = [child.name, child.year_of_birth, child.level, child.repetition]
                        result.set_updated(fields_before, fields_after)
                    else:
                        result.set_not_modified()
                elif children.count() > 1:
                    result.set_error('There is more than one child with name "{name}" in the family "{family}"')
                else:
                    child = Child.objects.create(name=name, year_of_birth=year_of_birth, repetition=repetition, family=family)
                    result.set_created()
            else:
                result.set_not_processed()

        except Exception as e:
            print(traceback.format_exc())
            result.set_error(f'Exception: {e}')

        return child, result
