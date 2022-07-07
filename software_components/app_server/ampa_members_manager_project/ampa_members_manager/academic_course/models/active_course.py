from django.db import models
from django.db.models import SET_NULL
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.academic_course.models.academic_course import AcademicCourse


class ActiveCourse(models.Model):
    course = models.ForeignKey(to=AcademicCourse, on_delete=SET_NULL, null=True, verbose_name=_("Course"))

    class Meta:
        verbose_name = _('Active course')
        verbose_name_plural = _("Active course")

    def __str__(self) -> str:
        return "ActiveCourse"

    def save(self, *args, **kwargs):
        self.pk = 1
        super(ActiveCourse, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # active course shouldn't be deleted'

    @classmethod
    def load(cls) -> AcademicCourse:
        established_course = cls.objects.get(pk=1)
        return established_course.course
