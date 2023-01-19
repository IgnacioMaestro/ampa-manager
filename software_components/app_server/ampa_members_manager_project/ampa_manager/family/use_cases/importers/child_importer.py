from ampa_manager.academic_course.models.level import Level
from ampa_manager.family.models.child import Child
from ampa_manager.management.commands.importers.import_model_result import ImportModelResult


class ChildImporter:

    @staticmethod
    def import_child(family, name: str, level: str, year_of_birth: int) -> ImportModelResult:
        result = ImportModelResult(Child.__name__, [name, level, year_of_birth])

        repetition = Level.calculate_repetition(level, year_of_birth)

        fields_ok, error = ChildImporter.validate_fields(name, year_of_birth, repetition)
        if fields_ok:
            child = family.find_child(name)
            if child:
                if child.is_modified(year_of_birth, repetition):
                    fields_before, fields_after = child.update(year_of_birth, repetition)
                    result.set_updated(child, fields_before, fields_after)
                else:
                    result.set_not_modified(child)
            else:
                child = Child.objects.create(name=name, year_of_birth=year_of_birth, repetition=repetition, family=family)
                result.set_created(child)
        else:
            result.set_error(error)

        return result

    @staticmethod
    def validate_fields(name, year_of_birth, repetition):
        if not name or type(name) != str:
            return False, f'Wrong name: {name} ({type(name)})'
        if year_of_birth is None or type(year_of_birth) != int:
            return False, f'Wrong year of birth: {year_of_birth} ({type(year_of_birth)})'
        if repetition is None or type(repetition) != int:
            return False, f'Wrong repetition: {repetition} ({type(repetition)})'
        return True, None
