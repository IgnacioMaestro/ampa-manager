from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class AcademicCourse(models.Model):
    HH2_YEARS_SINCE_BIRTH = 2
    HH3_YEARS_SINCE_BIRTH = 3
    HH4_YEARS_SINCE_BIRTH = 4
    HH5_YEARS_SINCE_BIRTH = 5
    LH1_YEARS_SINCE_BIRTH = 6
    LH2_YEARS_SINCE_BIRTH = 7
    LH3_YEARS_SINCE_BIRTH = 8
    LH4_YEARS_SINCE_BIRTH = 9
    LH5_YEARS_SINCE_BIRTH = 10
    LH6_YEARS_SINCE_BIRTH = 11

    initial_year = models.IntegerField(
        unique=True, validators=[MinValueValidator(1000), MaxValueValidator(3000)], verbose_name=_("Initial year"))
    fee = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Fee"))

    class Meta:
        verbose_name = _('Academic course')
        verbose_name_plural = _('Academic courses')

    def __str__(self) -> str:
        return f'{str(self.initial_year)}-{str(self.initial_year + 1)}'
