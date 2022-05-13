from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import CASCADE

from ampa_members_manager.academic_course.models.academic_course import AcademicCourse


class Fee(models.Model):
    amount = models.IntegerField(validators=[MinValueValidator(0)])
    year = models.ForeignKey(to=AcademicCourse, on_delete=CASCADE)

    def __str__(self) -> str:
        return f'{str(self.year)}'
