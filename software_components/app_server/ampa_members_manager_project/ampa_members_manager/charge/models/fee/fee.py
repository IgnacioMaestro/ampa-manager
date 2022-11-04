from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.academic_course.models.academic_course import AcademicCourse


class Fee(models.Model):
    academic_course = models.OneToOneField(to=AcademicCourse, on_delete=CASCADE)
    amount = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Fee"))

    def __str__(self) -> str:
        return str(self.academic_course)
