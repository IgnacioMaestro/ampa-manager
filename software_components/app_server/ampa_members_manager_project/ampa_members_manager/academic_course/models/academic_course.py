from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class AcademicCourse(models.Model):
    initial_year = models.IntegerField(
        unique=True, validators=[MinValueValidator(1000), MaxValueValidator(3000)], verbose_name=_("Initial year"))
    fee = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Fee"))

    class Meta:
        verbose_name = _('Academic course')
        verbose_name_plural = _('Academic courses')

    def __str__(self) -> str:
        return f'{str(self.initial_year)}-{str(self.initial_year + 1)}'
