from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext as _


class AcademicCourse(models.Model):
    initialYear = models.IntegerField(unique=True, validators=[MinValueValidator(1000), MaxValueValidator(3000)],
                                      verbose_name=_("Initial year"))
    fee = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Fee"))

    class Meta:
        verbose_name = _('Academic course')
        verbose_name_plural = _('Academic courses')

    def __str__(self) -> str:
        return f'{str(self.initialYear)}-{str(self.initialYear + 1)}'
