from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from ampa_manager.academic_course.models.level_constants import LevelConstants


class ChildImportData(models.Model):
    name = models.CharField(max_length=500, verbose_name=_("Name"))
    year_of_birth = models.IntegerField(
        validators=[MinValueValidator(1000), MaxValueValidator(3000)], verbose_name=_("Year of birth"))
    level = models.IntegerField(choices=LevelConstants.obtain_choices(), verbose_name=_("Level"))

    class Meta:
        abstract = True
        verbose_name = _('Child import data')
        verbose_name_plural = _('Child import data')
