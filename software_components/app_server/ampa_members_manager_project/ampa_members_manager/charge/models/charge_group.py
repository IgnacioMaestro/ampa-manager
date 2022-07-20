from __future__ import annotations

from django.db import models, transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.activity.models.single_activity import SingleActivity
from ampa_members_manager.charge.no_single_activity_error import NoSingleActivityError


class ChargeGroup(models.Model):
    single_activities = models.ManyToManyField(to=SingleActivity, verbose_name=_("Single activities"))

    class Meta:
        verbose_name = _('Charge group')
        verbose_name_plural = _('Charge groups')
    
    def __str__(self) -> str:
        return ', '.join(str(sa) for sa in self.single_activities.all())

    @classmethod
    def create_filled_charge_group(cls, single_activities: QuerySet[SingleActivity]) -> ChargeGroup:
        if not single_activities.exists():
            raise NoSingleActivityError

        with transaction.atomic():
            charge_group: ChargeGroup = ChargeGroup.objects.create()
            charge_group.single_activities.set(single_activities)
            return charge_group
