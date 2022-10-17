from typing import Optional
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import CASCADE, Manager
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.academic_course.models.level import Level
from ampa_members_manager.family.models.child_queryset import ChildQuerySet


class Child(models.Model):
    name = models.CharField(max_length=500, verbose_name=_("Name"))
    year_of_birth = models.IntegerField(validators=[MinValueValidator(1000), MaxValueValidator(3000)],
                                        verbose_name=_("Year of birth"))
    repetition = models.IntegerField(default=0, verbose_name=_("Repetition"))
    family = models.ForeignKey(to='Family', on_delete=CASCADE, verbose_name=_("Family"))

    objects = Manager.from_queryset(ChildQuerySet)()

    class Meta:
        verbose_name = _('Child')
        verbose_name_plural = _('Children')
        constraints = [
            models.UniqueConstraint(fields=['name', 'family'], name='unique_child_name_in_a_family'),]

    @property
    def full_name(self) -> str:
        return f'{self.name} {str(self.family)}'

    def __str__(self) -> str:
        return self.full_name
    
    def get_level_name(self) -> Optional[Level]:
        active_course = ActiveCourse.load()
        years_since_birth = active_course.initial_year - self.year_of_birth

        return Level.get_level_name_by_age(years_since_birth - self.repetition)
    
    def clean(self):
        if self.name:
            self.name = self.name.title().strip()

    @staticmethod
    def get_children_ids(min_age, max_age):
        return [c.id for c in Child.objects.by_age_range(min_age, max_age)]
