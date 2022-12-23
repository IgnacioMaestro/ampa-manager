from __future__ import annotations

from django.db import models, transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from ampa_members_manager.activity.models.activity_period import ActivityPeriod
from ampa_members_manager.charge.no_activity_period_error import NoActivityPeriodError


class ActivityRemittance(models.Model):
    name = models.CharField(max_length=300, verbose_name=_("Name"))
    identifier = models.CharField(max_length=40, null=True, blank=True, verbose_name=_("Identifier"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    activity_periods = models.ManyToManyField(to=ActivityPeriod, verbose_name=_("Activity periods"))

    class Meta:
        verbose_name = _('Activity remittance')
        verbose_name_plural = _('Activity remittances')
        db_table = 'activity_remittance'

    def __str__(self) -> str:
        return self.complete_name

    @property
    def complete_name(self) -> str:
        return self.name + '_' + self.created_at.strftime("%Y%m%d_%H%M%S")

    def get_admin_url(self):
        return reverse('admin:%s_%s_change' % (self._meta.app_label, self._meta.model_name), args=[self.id])

    @classmethod
    def create_filled(cls, activity_periods: QuerySet[ActivityPeriod]) -> ActivityRemittance:
        if not activity_periods.exists():
            raise NoActivityPeriodError

        with transaction.atomic():
            name: str = activity_periods.first().name
            activity_remittance: ActivityRemittance = ActivityRemittance.objects.create(name=name)
            activity_remittance.activity_periods.set(activity_periods)
            return activity_remittance

    def get_receipt_count(self, state):
        return self.activityreceipt_set.filter(state=state).count()
