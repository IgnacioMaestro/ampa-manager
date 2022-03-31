from django.db import models
from django.db.models import CASCADE

from ampa_members_manager.academic_course.models.academic_course import AcademicCourse
from ampa_members_manager.family.models.family import Family


class Membership(models.Model):
    family = models.ForeignKey(to=Family, on_delete=CASCADE)
    academic_course = models.ForeignKey(to=AcademicCourse, on_delete=CASCADE)

    def __str__(self) -> str:
        return f'{str(self.family)}-{str(self.academic_course)}'
