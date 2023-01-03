import traceback

from ampa_manager.academic_course.models.level import Level
from ampa_manager.family.models.child import Child
from ampa_manager.field_formatters.fields_formatter import FieldsFormatter
from ampa_manager.management.commands.imported_fields.child_imported_fields import ChildImportedFields
from ampa_manager.management.commands.results.import_member_result import ImportMemberResult


class ChildImporter:

    def __init__(self, sheet, columns_indexes):
        self.sheet = sheet
        self.columns_indexes = columns_indexes

    def import_child(self, row_index, child_number, family):
        child = None
        result = ImportMemberResult(Child.__name__, row_index)

        try:
            fields = self.import_fields(row_index, child_number)
            result.fields_excel = fields.get_list()

            if fields.name and family:
                repetition = Level.calculate_repetition(fields.level, fields.year_of_birth)

                child, error = family.find_child(fields.name)
                if child:
                    if ChildImporter.is_modified(child, fields.year_of_birth, repetition):
                        fields_before, fields_after = ChildImporter.update(child, fields.year_of_birth, repetition)
                        result.set_updated(fields_before, fields_after)
                    else:
                        result.set_not_modified()
                elif error:
                    result.set_error(error)
                else:
                    fields_ok, error = ChildImporter.validate_fields(fields.name, fields.year_of_birth, repetition)
                    if fields_ok:
                        child = Child.objects.create(name=fields.name, year_of_birth=fields.year_of_birth,
                                                     repetition=repetition, family=family)
                        result.set_created()
                    else:
                        result.set_error(error)
            else:
                result.set_not_processed()

        except Exception as e:
            print(traceback.format_exc())
            result.set_error(f'Exception: {e}')

        return child, result

    def import_fields(self, row_index, child_number) -> ChildImportedFields:
        name = None
        year = None
        level = None

        if child_number in [1, 2, 3, 4, 5]:
            name_index = None
            year_index = None
            level_index = None

            if child_number == 1:
                name_index = self.columns_indexes['child1_name']
                year_index = self.columns_indexes['child1_year']
                level_index = self.columns_indexes['child1_level']
            elif child_number == 2:
                name_index = self.columns_indexes['child2_name']
                year_index = self.columns_indexes['child2_year']
                level_index = self.columns_indexes['child2_level']
            elif child_number == 3:
                name_index = self.columns_indexes['child3_name']
                year_index = self.columns_indexes['child3_year']
                level_index = self.columns_indexes['child3_level']
            elif child_number == 4:
                name_index = self.columns_indexes['child4_name']
                year_index = self.columns_indexes['child4_year']
                level_index = self.columns_indexes['child4_level']
            elif child_number == 5:
                name_index = self.columns_indexes['child5_name']
                year_index = self.columns_indexes['child5_year']
                level_index = self.columns_indexes['child5_level']

            name = FieldsFormatter.clean_name(self.sheet.cell_value(rowx=row_index, colx=name_index))
            year = FieldsFormatter.clean_integer(self.sheet.cell_value(rowx=row_index, colx=year_index))
            level = Level.parse_level(self.sheet.cell_value(rowx=row_index, colx=level_index))

        return ChildImportedFields(name, year, level)

    @staticmethod
    def is_modified(child, year_of_birth, repetition):
        return child.year_of_birth != year_of_birth or child.repetition != repetition

    @staticmethod
    def update(child, year_of_birth, repetition):
        fields_before = [child.name, child.year_of_birth, child.level, child.repetition]
        child.year_of_birth = year_of_birth
        child.repetition = repetition
        child.save()
        fields_after = [child.name, child.year_of_birth, child.level, child.repetition]
        return fields_before, fields_after

    @staticmethod
    def validate_fields(name, year_of_birth, repetition):
        if not name or type(name) != str:
            return False, f'Wrong name: {name} ({type(name)})'
        if year_of_birth is None or type(year_of_birth) != int:
            return False, f'Wrong year of birth: {year_of_birth} ({type(year_of_birth)})'
        if repetition is None or type(repetition) != int:
            return False, f'Wrong repetition: {repetition} ({type(repetition)})'
        return True, None
