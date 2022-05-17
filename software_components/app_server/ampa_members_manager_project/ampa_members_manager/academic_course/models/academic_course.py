from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext as _


class AcademicCourse(models.Model):
    initialYear = models.IntegerField(verbose_name=_("Initial year"), unique=True, validators=[MinValueValidator(1000), MaxValueValidator(3000)])
    fee = models.PositiveIntegerField(verbose_name=_("Fee"), null=True, blank=True)

    class Meta:
        verbose_name = _('Academic course')
        verbose_name_plural = _('Academic courses')

    def __str__(self) -> str:
        return f'{str(self.initialYear)}-{str(self.initialYear + 1)}'
