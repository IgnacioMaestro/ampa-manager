from django.db import models
from django.db.models import CASCADE

from ampa_members_manager.academic_course.models.academic_course import AcademicCourse


class Funding(models.IntegerChoices):
    NO_FUNDING = 1
    CULTURAL = 2
    SPORT = 3


class Activity(models.Model):
    name = models.CharField(max_length=100)
    academic_course = models.ForeignKey(to=AcademicCourse, on_delete=CASCADE)
    funding = models.IntegerField(choices=Funding.choices)

    class Meta:
        abstract = True
