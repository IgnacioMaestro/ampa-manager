from typing import Optional

from django.utils.translation import gettext_lazy as _

from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.academic_course.models.level import Level
from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult
from ampa_manager.family.models.child import Child


class ChildImporter:

    def __init__(self, family, name: str, level: str, year_of_birth: int):
        self.result = ImportModelResult(Child.__name__)
        self.family = family
        self.name = name
        self.level = level
        self.year_of_birth = year_of_birth
        self.repetition = None
        self.child = None

    def import_child(self) -> ImportModelResult:
        error_message = self.validate_fields()
        if error_message is None:
            self.manage_level_and_year_of_birth()
            self.manage_repetition()

            self.child = self.family.find_child(self.name)
            if self.child:
                self.manage_found_child()
            elif self.level or self.year_of_birth:
                self.manage_not_found_child()
            elif not self.level:
                self.result.set_error(_('Missing level'))
            elif not self.year_of_birth:
                self.result.set_error(_('Missing year of birth'))
        else:
            self.result.set_error(error_message)

        return self.result

    def manage_level_and_year_of_birth(self) -> Optional[int]:
        if self.level and not self.year_of_birth:
            current_course = ActiveCourse.load()
            self.year_of_birth = current_course.initial_year - Level.get_age_by_level(self.level)

            if self.year_of_birth:
                self.result.add_warning(_('Year of birth calculated') + f' ({self.level} -> {self.year_of_birth})')
            else:
                self.result.set_error(_('Unable to calculate year of birth'))
                return

        if not self.level and self.year_of_birth:
            current_course = ActiveCourse.load()
            age = current_course.initial_year - self.year_of_birth
            self.level = Level.get_level_by_age(age)

            if self.level:
                self.result.add_warning(_('Level calculated') + f' ({self.year_of_birth} -> {self.level})')
            else:
                self.result.set_error(_('Unable to calculate level'))
                return

    def manage_not_found_child(self):
        child = Child.objects.create(name=self.name, year_of_birth=self.year_of_birth, repetition=self.repetition,
                                     family=self.family)
        self.result.set_created(child)

    def manage_repetition(self):
        if self.level and self.year_of_birth:
            self.repetition = Level.calculate_repetition(self.level, self.year_of_birth)
            if self.repetition is None or self.repetition < 0:
                self.result.set_error(_('Wrong level or year of birth') + f' ({self.level}, {self.year_of_birth})')

    def manage_found_child(self):
        if self.level and self.year_of_birth:
            if self.child_is_modified():
                values_before = [self.child.year_of_birth, self.child.repetition]

                if self.year_of_birth is not None:
                    self.child.year_of_birth = self.year_of_birth

                if self.repetition is not None:
                    self.child.repetition = self.repetition

                self.child.save()

                values_after = [self.child.year_of_birth, self.child.repetition]
                self.result.set_updated(self.child, values_before, values_after)
            else:
                self.result.set_not_modified(self.child)
        else:
            self.result.set_not_modified(self.child)

    def child_is_modified(self):
        return self.year_of_birth != self.child.year_of_birth or self.repetition != self.child.repetition

    def validate_fields(self) -> Optional[str]:
        if not self.family:
            return 'Missing family'
        if not self.name or not isinstance(self.name, str):
            return f'Missing/Wrong name: {self.name} ({type(self.name)})'
        if self.level is not None and not Level.is_valid(self.level):
            return f'Wrong level: {self.level} ({type(self.level)})'
        if self.year_of_birth is not None and not isinstance(self.year_of_birth, int):
            return f'Wrong year of birth: {self.year_of_birth} ({type(self.year_of_birth)})'
        return None
