from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext as _

from ampa_members_manager.academic_course.models.academic_course import AcademicCourse


class Funding(models.IntegerChoices):
    NO_FUNDING = 1
    CULTURAL = 2
    SPORT = 3


class Activity(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=100)
    academic_course = models.ForeignKey(verbose_name=_("Academic course"), to=AcademicCourse, on_delete=CASCADE)
    funding = models.IntegerField(verbose_name=_("Funding"), choices=Funding.choices)

    class Meta:
        abstract = True
        verbose_name = _('Activity')
        verbose_name_plural = _('Activities')
