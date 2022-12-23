from __future__ import annotations

from django.db import models, transaction
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_members_manager.charge.no_after_school_edition_error import NoAfterSchoolEditionError


class AfterSchoolRemittance(models.Model):
    name = models.CharField(max_length=300, null=True, blank=True, verbose_name=_("Name"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    after_school_editions = models.ManyToManyField(to=AfterSchoolEdition, verbose_name=_("AfterSchoolEditions"), related_name="after_school_remittance")

    class Meta:
        verbose_name = _('AfterSchool remittance')
        verbose_name_plural = _('AfterSchool remittances')

    def __str__(self) -> str:
        return self.complete_name

    def get_admin_url(self):
        return reverse('admin:%s_%s_change' % (self._meta.app_label, self._meta.model_name), args=[self.id])

    @property
    def complete_name(self) -> str:
        time_name = '_' + self.created_at.strftime("%Y%m%d_%H%M%S")
        if self.name:
            return self.name + time_name
        return time_name

    @classmethod
    def create_filled(cls, after_school_editions: QuerySet[AfterSchoolEdition]) -> AfterSchoolRemittance:
        if not after_school_editions.exists():
            raise NoAfterSchoolEditionError

        with transaction.atomic():
            after_school_remittance: AfterSchoolRemittance = AfterSchoolRemittance.objects.create()
            after_school_remittance.after_school_editions.set(after_school_editions)
            return after_school_remittance
