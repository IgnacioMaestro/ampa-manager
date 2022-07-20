from __future__ import annotations

from django.db import models, transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.activity.models.single_activity import SingleActivity
from ampa_members_manager.charge.no_single_activity_error import NoSingleActivityError


class ActivityRemittance(models.Model):
    single_activities = models.ManyToManyField(to=SingleActivity, verbose_name=_("Single activities"))

    class Meta:
        verbose_name = _('Activity Remittance')
        verbose_name_plural = _('Activity Remittances')

    @classmethod
    def create_filled_charge_group(cls, single_activities: QuerySet[SingleActivity]) -> ActivityRemittance:
        if not single_activities.exists():
            raise NoSingleActivityError

        with transaction.atomic():
            charge_group: ActivityRemittance = ActivityRemittance.objects.create()
            charge_group.single_activities.set(single_activities)
            return charge_group
