from typing import Optional

from django.db import models
from django.db.models import SET_NULL
from django.utils.translation import gettext_lazy as _

from ampa_manager.academic_course.models.academic_course import AcademicCourse


class ActiveCourse(models.Model):
    course = models.ForeignKey(to=AcademicCourse, on_delete=SET_NULL, null=True, verbose_name=_("Course"))

    class Meta:
        verbose_name = _('Active course')
        verbose_name_plural = _("Active course")
        db_table = 'active_course'

    def __str__(self) -> str:
        return str(self.course)

    def save(self, *args, **kwargs):
        self.pk = 1
        super(ActiveCourse, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # active course shouldn't be deleted

    @classmethod
    def get_previous(cls) -> Optional[AcademicCourse]:
        try:
            return AcademicCourse.objects.get(initial_year=cls.get_active_course_initial_year()-1)
        except AcademicCourse.DoesNotExist:
            return None

    @classmethod
    def load(cls) -> AcademicCourse:
        established_course = cls.objects.get(pk=1)
        return established_course.course

    @classmethod
    def get_active_course_initial_year(cls) -> int:
        return cls.load().initial_year
