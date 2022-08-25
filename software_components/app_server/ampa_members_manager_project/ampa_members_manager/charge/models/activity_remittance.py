from __future__ import annotations

from django.db import models, transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.activity.models.activity_period import ActivityPeriod
from ampa_members_manager.charge.no_payable_part_error import NoActivityPeriodError


class ActivityRemittance(models.Model):
    name = models.CharField(max_length=300, verbose_name=_("Name"))
    identifier = models.CharField(max_length=40, null=True, blank=True,verbose_name=_("Identifier"))
    created_at = models.DateTimeField(auto_now_add=True)
    payable_parts = models.ManyToManyField(to=ActivityPeriod, verbose_name=_("Activity Payable Parts"))

    class Meta:
        verbose_name = _('Activity Remittance')
        verbose_name_plural = _('Activity Remittances')

    def __str__(self) -> str:
        return self.complete_name

    @property
    def complete_name(self) -> str:
        return self.name + '_' + self.created_at.strftime("%Y%m%d_%H%M%S")

    @classmethod
    def create_filled(cls, payable_parts: QuerySet[ActivityPeriod]) -> ActivityRemittance:
        if not payable_parts.exists():
            raise NoActivityPeriodError

        with transaction.atomic():
            name: str = payable_parts.first().name
            activity_remittance: ActivityRemittance = ActivityRemittance.objects.create(name=name)
            activity_remittance.payable_parts.set(payable_parts)
            return activity_remittance
