from django.db import models
from django.db.models import CASCADE, Manager
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.charge.models.membership_remittance_queryset import MembershipRemittanceQuerySet
from ampa_manager.charge.models.nameable_with_date import NameableWithDate


class MembershipRemittance(NameableWithDate, models.Model):
    course = models.ForeignKey(to=AcademicCourse, on_delete=CASCADE, verbose_name=_("AcademicCourse"))

    objects = Manager.from_queryset(MembershipRemittanceQuerySet)()

    class Meta:
        verbose_name = _('Membership remittance')
        verbose_name_plural = _('Membership remittances')
        db_table = 'membership_remittance'

    def __str__(self) -> str:
        return self.complete_name

    @property
    def complete_name(self) -> str:
        return f'{self.course} - {self.name} ({self.created_at.strftime("%d/%m/%y")})'

    def get_admin_url(self):
        return reverse('admin:%s_%s_change' % (self._meta.app_label, self._meta.model_name), args=[self.id])
