from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.academic_course.models.academic_course import AcademicCourse


class Funding(models.IntegerChoices):
    NO_FUNDING = (1, _('No funding'))
    CULTURAL = (2, _('Cultural'))
    SPORT = (3, _('Sport'))


class Activity(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    academic_course = models.ForeignKey(to=AcademicCourse, on_delete=CASCADE, verbose_name=_("Academic course"))
    funding = models.IntegerField(choices=Funding.choices, verbose_name=_("Funding"))

    class Meta:
        abstract = True
        verbose_name = _('Activity')
        verbose_name_plural = _('Activities')
