from django.db import models
from django.db.models import CASCADE

from ampa_members_manager.academic_course.models.academic_course import AcademicCourse


class Assignment(models.IntegerChoices):
    FAMILIAR = 1
    INDIVIDUAL = 2


class Funding(models.IntegerChoices):
    NO_FUNDING = 1
    CULTURAL = 2
    SPORT = 3


class Activity(models.Model):
    name = models.CharField(max_length=100)
    academic_course = models.ForeignKey(to=AcademicCourse, on_delete=CASCADE)
    assignment = models.IntegerField(choices=Assignment.choices)
    funding = models.IntegerField(choices=Funding.choices)

    class Meta:
        abstract = True
