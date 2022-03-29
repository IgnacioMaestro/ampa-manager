from django.db import models


class AcademicCourse(models.Model):
    initialYear = models.IntegerField(unique=True)

    def __str__(self) -> str:
        return f'{str(self.initialYear)}-{str(self.initialYear + 1)}'
