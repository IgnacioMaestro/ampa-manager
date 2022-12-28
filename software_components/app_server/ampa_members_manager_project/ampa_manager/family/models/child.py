import re

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import CASCADE, Manager
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from ampa_manager.academic_course.models.level import Level
from ampa_manager.family.models.child_queryset import ChildQuerySet
from ampa_manager.management.commands.import_command.surnames import SURNAMES


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

    def clean(self):
        if self.name:
            self.name = self.name.title().strip()

    @staticmethod
    def get_children_ids(min_age, max_age):
        return [c.id for c in Child.objects.of_age_in_range(min_age, max_age)]

    @staticmethod
    def find(family, name):
        children = Child.objects.with_name_and_of_family(name, family)
        if children.count() == 1:
            return children[0]
        return None

    @staticmethod
    def fix_accents():
        for child in Child.objects.all():
            for wrong, right in SURNAMES.items():
                pattern = rf'\b{wrong}\b'
                if re.search(pattern, child.name):
                    before = child.name
                    child.name = re.sub(pattern, right, child.name)
                    child.save(update_fields=['name'])
                    print(f'Child name fixed: {before} -> {child.name}')
