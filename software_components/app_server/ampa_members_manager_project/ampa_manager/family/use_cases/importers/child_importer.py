from typing import Optional

from django.utils.translation import gettext_lazy as _

from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.academic_course.models.level import Level
from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult, ModifiedField
from ampa_manager.family.models.child import Child


class ChildImporter:

    def __init__(self, family, name: str, level: str, year_of_birth: int, compulsory: bool):
        self.result: ImportModelResult = ImportModelResult(Child)
        self.family = family
        self.name = name
        self.level = level
        self.year_of_birth = year_of_birth
        self.repetition = None
        self.compulsory = compulsory
        self.child = None

    def import_child(self) -> ImportModelResult:
        try:
            if not self.compulsory and self.all_child_fields_are_empty():
                self.result.set_omitted()
                return self.result

            error_message = self.validate_fields()
            if error_message is None:

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
        except Exception as e:
            self.result.set_error(str(e))

        return self.result

    def all_child_fields_are_empty(self):
        return not self.name and not self.level and not self.year_of_birth

    def manage_not_found_child(self):
        child = Child.objects.create(name=self.name, year_of_birth=self.year_of_birth, repetition=self.repetition,
                                     family=self.family)
        self.result.set_created(child)

    def manage_found_child(self):
        if self.level and self.year_of_birth and self.child_is_modified():
            modified_fields = []

            if self.year_of_birth is not None and self.year_of_birth != self.child.year_of_birth:
                modified_fields.append(ModifiedField(_('Year of birth'), self.child.year_of_birth, self.year_of_birth))
                self.child.year_of_birth = self.year_of_birth

            if self.repetition is not None and self.repetition != self.child.repetition:
                modified_fields.append(ModifiedField(_('Repetition'), self.child.repetition, self.repetition))
                self.child.repetition = self.repetition

            self.child.save()

            self.result.set_updated(self.child, modified_fields)
        else:
            self.result.set_not_modified(self.child)

    def child_is_modified(self):
        return ((self.year_of_birth is not None and self.year_of_birth != self.child.year_of_birth) or
                (self.repetition is not None and self.repetition != self.child.repetition))

    def validate_fields(self) -> Optional[str]:
        if not self.family:
            return _('Missing family')

        if not self.name or not isinstance(self.name, str):
            return _('Missing/Wrong name') + f' ({self.name})'

        if self.level is not None and not Level.is_valid(self.level):
            return _('Wrong level') + f' ({self.level})'

        if self.year_of_birth is not None and not isinstance(self.year_of_birth, int):
            return _('Wrong year of birth') + f': ({self.year_of_birth})'

        if self.level and not self.year_of_birth:
            current_course = ActiveCourse.load()
            self.year_of_birth = current_course.initial_year - Level.get_age_by_level(self.level)

            if self.year_of_birth:
                self.result.add_warning(_('Year of birth calculated') + f' ({self.level} -> {self.year_of_birth})', minor=True)
            else:
                return _('Unable to calculate year of birth')

        if not self.level and self.year_of_birth:
            current_course = ActiveCourse.load()
            age = current_course.initial_year - self.year_of_birth
            self.level = Level.get_level_by_age(age)

            if self.level:
                self.result.add_warning(_('Level calculated') + f' ({self.year_of_birth} -> {self.level})', minor=True)
            else:
                return _('Unable to calculate level')

        if self.level and self.year_of_birth:
            self.repetition = Level.calculate_repetition(self.level, self.year_of_birth)
            if self.repetition is None or self.repetition < 0:
                return _('Wrong level or year of birth') + f' ({self.level}, {self.year_of_birth})'

        return None
