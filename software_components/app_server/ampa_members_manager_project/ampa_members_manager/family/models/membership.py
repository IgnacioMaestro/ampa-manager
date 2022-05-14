from django.db import models
from django.db.models import CASCADE

from ampa_members_manager.academic_course.models.academic_course import AcademicCourse
from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.family.models.child import Child
from ampa_members_manager.family.models.family import Family


class Membership(models.Model):
    family = models.ForeignKey(to=Family, on_delete=CASCADE)
    academic_course = models.ForeignKey(to=AcademicCourse, on_delete=CASCADE)

    def __str__(self) -> str:
        return f'{str(self.family)}-{str(self.academic_course)}'

    @classmethod
    def is_membership_family(cls, family: Family) -> bool:
        return Membership.objects.filter(family=family, academic_course=ActiveCourse.load()).exists()

    @classmethod
    def is_membership_child(cls, child: Child) -> bool:
        return Membership.objects.filter(family=child.family, academic_course=ActiveCourse.load()).exists()
