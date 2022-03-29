from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class AcademicCourse(models.Model):
    initialYear = models.IntegerField(unique=True, validators=[MinValueValidator(1000), MaxValueValidator(3000)])

    def __str__(self) -> str:
        return f'{str(self.initialYear)}-{str(self.initialYear + 1)}'
