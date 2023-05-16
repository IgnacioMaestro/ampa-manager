from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.academic_course.models.level import Level
from ampa_manager.family.models.child import Child
from ampa_manager.family.use_cases.importers.fields_changes import FieldsChanges
from ampa_manager.utils.excel.import_model_result import ImportModelResult


class ChildImporter:

    @staticmethod
    def import_child(family, name: str, level: str, year_of_birth: int) -> ImportModelResult:
        result = ImportModelResult(Child.__name__, [name, level, year_of_birth])

        fields_ok, error = ChildImporter.validate_fields(family, name, level, year_of_birth)
        if fields_ok:
            child = family.find_child(name)
            if child:
                if level and year_of_birth:
                    repetition = Level.calculate_repetition(level, year_of_birth)
                    if repetition >= 0:
                        if child.is_modified(year_of_birth, repetition):
                            fields_changes: FieldsChanges = child.update(year_of_birth, repetition)
                            result.set_updated(child, fields_changes)
                        else:
                            result.set_not_modified(child)
                    else:
                        result.set_error('Wrong level or year of birth')
                else:
                    result.set_not_modified(child)
            elif level or year_of_birth:
                if level and not year_of_birth:
                    current_course = ActiveCourse.load()
                    year_of_birth = current_course.initial_year - Level.get_age_by_level(level)
                    result.add_warning(f'Missing year of birth calculated from level: {level} -> {year_of_birth}')
                if not level and year_of_birth:
                    current_course = ActiveCourse.load()
                    age = current_course.initial_year - year_of_birth
                    level = Level.get_level_by_age(age)
                    result.add_warning(f'Missing level calculated from year of birth: {year_of_birth} -> {level}')

                repetition = Level.calculate_repetition(level, year_of_birth)
                if repetition >= 0:
                    child = Child.objects.create(name=name, year_of_birth=year_of_birth, repetition=repetition,
                                                 family=family)
                    result.set_created(child)
                else:
                    result.set_error('Wrong level or year of birth')
            elif not level:
                result.set_error('Missing level')
            elif not year_of_birth:
                result.set_error('Missing year of birth')
        else:
            result.set_error(error)

        return result

    @staticmethod
    def validate_fields(family, name, level, year_of_birth):
        if not family:
            return False, f'Missing family'
        if not name or type(name) != str:
            return False, f'Missing/Wrong name: {name} ({type(name)})'
        if level is not None and not Level.is_valid(level):
            return False, f'Missing/Wrong repetition: {level} ({type(level)})'
        if year_of_birth is not None and type(year_of_birth) != int:
            return False, f'Missing/Wrong year of birth: {year_of_birth} ({type(year_of_birth)})'

        return True, None
