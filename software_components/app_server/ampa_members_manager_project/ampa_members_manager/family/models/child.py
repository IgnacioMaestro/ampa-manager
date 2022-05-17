from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext as _

from ampa_members_manager.family.models.family import Family


class Child(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=500)
    year_of_birth = models.IntegerField(verbose_name=_("Year of birth"), validators=[MinValueValidator(1000), MaxValueValidator(3000)])
    repetition = models.IntegerField(verbose_name=_("Repetition"), default=0)
    family = models.ForeignKey(verbose_name=_("Family"), to=Family, on_delete=CASCADE)

    class Meta:
        verbose_name = _('Child')
        verbose_name_plural = _('Children')

    @property
    def full_name(self) -> str:
        return f'{self.name} {str(self.family)}'

    def __str__(self) -> str:
        return self.full_name
