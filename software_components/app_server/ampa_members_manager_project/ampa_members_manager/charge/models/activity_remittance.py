from __future__ import annotations

from django.db import models, transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.activity.models.single_activity import SingleActivity
from ampa_members_manager.charge.no_single_activity_error import NoSingleActivityError


class ActivityRemittance(models.Model):
    name = models.CharField(max_length=300, verbose_name=_("Name"))
    created_at = models.DateTimeField(auto_now_add=True)
    single_activities = models.ManyToManyField(to=SingleActivity, verbose_name=_("Single activities"))

    class Meta:
        verbose_name = _('Activity Remittance')
        verbose_name_plural = _('Activity Remittances')

    def __str__(self) -> str:
        return self.complete_name

    @property
    def complete_name(self) -> str:
        return self.name + '_' + self.created_at.strftime("%Y%m%d_%H%M%S")

    @classmethod
    def create_filled(cls, single_activities: QuerySet[SingleActivity]) -> ActivityRemittance:
        if not single_activities.exists():
            raise NoSingleActivityError

        with transaction.atomic():
            activity_remittance: ActivityRemittance = ActivityRemittance.objects.create()
            activity_remittance.single_activities.set(single_activities)
            return activity_remittance
