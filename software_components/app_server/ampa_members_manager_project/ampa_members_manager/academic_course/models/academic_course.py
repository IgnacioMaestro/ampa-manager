from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class AcademicCourse(models.Model):
    initial_year = models.IntegerField('Initial year', unique=True, validators=[MinValueValidator(1000), MaxValueValidator(3000)])
    fee = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self) -> str:
        return f'{str(self.initial_year)}-{str(self.initial_year + 1)}'
