from django.db import models
from django.db.models import CASCADE, Manager
from django.utils.translation import gettext_lazy as _

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.membership_queryset import MembershipQuerySet


class Membership(models.Model):
    family = models.ForeignKey(to=Family, on_delete=CASCADE, verbose_name=_("Family"))
    academic_course = models.ForeignKey(to=AcademicCourse, on_delete=CASCADE, verbose_name=_("Academic course"))

    objects = Manager.from_queryset(MembershipQuerySet)()

    class Meta:
        verbose_name = _('Membership')
        verbose_name_plural = _('Membership')
        db_table = 'membership'
        constraints = [
            models.UniqueConstraint(fields=['academic_course', 'family'], name='unique_family_membership_for_course'), ]

    def __str__(self) -> str:
        return f'{str(self.family)}-{str(self.academic_course)}'

    @classmethod
    def is_member_family(cls, family: Family) -> bool:
        return Membership.objects.of_family(family).exists()

    @classmethod
    def is_member_child(cls, child: Child) -> bool:
        return Membership.objects.of_family(child.family).exists()

    @classmethod
    def make_member_for_active_course(cls, family: Family):
        member = Membership(family=family, academic_course=ActiveCourse.load())
        member.save()
