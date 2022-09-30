from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from ampa_members_manager.academic_course.models.academic_course import AcademicCourse


class MembershipRemittance(models.Model):
    identifier = models.CharField(max_length=40, null=True, blank=True, verbose_name=_("Identifier"))
    created_at = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey(to=AcademicCourse, on_delete=CASCADE, verbose_name=_("AcademicCourse"))

    class Meta:
        verbose_name = _('Membership remittance')
        verbose_name_plural = _('Membership remittances')

    def __str__(self) -> str:
        return self.complete_name

    @property
    def complete_name(self) -> str:
        return str(self.course) + ' - ' + self.created_at.strftime("%Y%m%d_%H%M%S")
    
    def get_admin_url(self):
        return reverse('admin:%s_%s_change' % (self._meta.app_label, self._meta.model_name), args = [self.id])
