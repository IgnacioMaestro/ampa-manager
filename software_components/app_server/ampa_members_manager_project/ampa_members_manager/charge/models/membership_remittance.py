from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.academic_course.models.academic_course import AcademicCourse


class MembershipRemittance(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey(to=AcademicCourse, on_delete=CASCADE, verbose_name=_("AcademicCourse"))

    def __str__(self) -> str:
        return self.complete_name

    @property
    def complete_name(self) -> str:
        return str(self.course) + '_' + self.created_at.strftime("%Y%m%d_%H%M%S")
