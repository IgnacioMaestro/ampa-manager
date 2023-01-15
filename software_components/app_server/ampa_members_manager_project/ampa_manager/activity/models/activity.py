from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.activity.models.funding import Funding
from ampa_manager.utils.fields_formatters import FieldsFormatters


class Activity(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Activity name"))
    academic_course = models.ForeignKey(to=AcademicCourse, on_delete=CASCADE, verbose_name=_("Academic course"))
    funding = models.IntegerField(choices=Funding.choices, verbose_name=_("Funding"))

    class Meta:
        verbose_name = _('Activity')
        verbose_name_plural = _('Activity')
        db_table = 'activity'

    def __str__(self) -> str:
        return f'{self.name}'

    def clean(self):
        if self.name:
            self.name = FieldsFormatters.clean_name(self.name)
