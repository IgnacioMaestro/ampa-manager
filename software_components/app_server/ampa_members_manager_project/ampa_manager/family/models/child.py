from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import CASCADE, Manager
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from ampa_manager.academic_course.models.level import Level
from ampa_manager.family.models.child_queryset import ChildQuerySet
from ampa_manager.management.commands.results.processing_state import ProcessingState
from ampa_manager.utils.fields_formatters import FieldsFormatters
from ampa_manager.utils.string_utils import StringUtils


class Child(TimeStampedModel):
    name = models.CharField(max_length=500, verbose_name=_("Name"))
    year_of_birth = models.IntegerField(
        validators=[MinValueValidator(1000), MaxValueValidator(3000)], verbose_name=_("Year of birth"))
    repetition = models.IntegerField(default=0, verbose_name=_("Repetition"))
    family = models.ForeignKey(to='Family', on_delete=CASCADE, verbose_name=_("Family"))

    objects = Manager.from_queryset(ChildQuerySet)()

    class Meta:
        verbose_name = _('Child')
        verbose_name_plural = _('Children')
        db_table = 'child'
        constraints = [
            models.UniqueConstraint(fields=['name', 'family'], name='unique_child_name_in_a_family'), ]

    @property
    def full_name(self) -> str:
        return f'{self.name} {str(self.family)}'

    def __str__(self) -> str:
        return self.full_name

    @property
    def level(self):
        return Level.get_level_by_age(self.school_age)

    @property
    def age(self):
        return Level.calculate_age(self.year_of_birth)

    @property
    def school_age(self):
        return self.age - self.repetition

    def clean_name(self):
        return FieldsFormatters.clean_name(self.cleaned_data['name'])

    def is_modified(self, year_of_birth, repetition):
        return self.year_of_birth != year_of_birth or self.repetition != repetition

    def update(self, year_of_birth, repetition):
        fields_before = [self.name, self.year_of_birth, self.level, self.repetition]
        self.year_of_birth = year_of_birth
        self.repetition = repetition
        self.save()
        fields_after = [self.name, self.year_of_birth, self.level, self.repetition]
        return fields_before, fields_after

    @staticmethod
    def get_children_ids(min_age, max_age):
        return [c.id for c in Child.objects.of_age_in_range(min_age, max_age)]

    def matches_name(self, name, strict=False):
        if self.name and name:
            if strict:
                if StringUtils.compare_ignoring_everything(self.name, name):
                    return True
            elif StringUtils.contains_any_word(self.name, name):
                return True
        return False

    @staticmethod
    def fix_names():
        for child in Child.objects.all():
            fixed_name = FieldsFormatters.clean_name(child.name)
            if fixed_name != child.name:
                print(f'Child name fixed: "{child.name}" -> "{fixed_name}"')
                child.name = fixed_name
                child.save(update_fields=['name'])


