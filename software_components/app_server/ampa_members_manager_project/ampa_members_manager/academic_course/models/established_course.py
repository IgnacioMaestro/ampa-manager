from django.db import models
from django.db.models import SET_NULL
from django.utils.translation import gettext as _

from ampa_members_manager.academic_course.models.academic_course import AcademicCourse


class EstablishedCourse(models.Model):
    course = models.ForeignKey(verbose_name=_('Course'), to=AcademicCourse, on_delete=SET_NULL, null=True)

    def __str__(self) -> str:
        return "SingletonEstablishedCourse"

    def save(self, *args, **kwargs):
        self.pk = 1
        super(EstablishedCourse, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls) -> AcademicCourse:
        established_course = cls.objects.get(pk=1)
        return established_course.course
