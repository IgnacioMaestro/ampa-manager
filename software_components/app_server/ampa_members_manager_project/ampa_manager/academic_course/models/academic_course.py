from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class AcademicCourse(models.Model):
    initial_year = models.IntegerField(
        unique=True, validators=[MinValueValidator(1000), MaxValueValidator(3000)], verbose_name=_("Initial year"))

    class Meta:
        verbose_name = _('Academic course')
        verbose_name_plural = _('Academic courses')
        db_table = 'academic_course'

    def __str__(self) -> str:
        initial_year = str(self.initial_year)[-2:]
        final_year = str(self.initial_year + 1)[-2:]
        return f'{initial_year}-{final_year}'
