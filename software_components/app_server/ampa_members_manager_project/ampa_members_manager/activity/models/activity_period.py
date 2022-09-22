from __future__ import annotations

from django.db import models
from django.db.models import CASCADE, QuerySet
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.activity.models.activity import Activity
from ampa_members_manager.activity.models.payment_type import PaymentType


class ActivityPeriod(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Period name"))
    price_for_member = models.DecimalField(max_digits=6, decimal_places=2, verbose_name=_("Price for members"))
    price_for_no_member = models.DecimalField(max_digits=6, decimal_places=2, verbose_name=_("Price for no members"))
    payment_type = models.IntegerField(choices=PaymentType.choices, verbose_name=_("Payment type"))
    activity = models.ForeignKey(to=Activity, on_delete=CASCADE, verbose_name=_("Activity"))

    class Meta:
        verbose_name = _('Activity Period')
        verbose_name_plural = _('Activity Periods')

    def __str__(self) -> str:
        return f'{self.activity} - {self.name}'

    def calculate_price(self, times: float, membership: bool) -> float:
        if membership:
            return self.calculate_price_membership(times)
        else:
            return self.calculate_price_no_membership(times)

    def calculate_price_no_membership(self, times):
        if self.payment_type == int(PaymentType.SINGLE):
            return float(self.price_for_no_member)
        else:
            return float(self.price_for_no_member) * times

    def calculate_price_membership(self, times):
        if self.payment_type == int(PaymentType.SINGLE):
            return float(self.price_for_member)
        else:
            return float(self.price_for_member) * times

    @classmethod
    def all_same_activity(cls, activity_periods: QuerySet[ActivityPeriod]) -> bool:
        if activity_periods.count() > 1:
            activity: Activity = activity_periods.first().activity
            activity_period: ActivityPeriod
            for activity_period in activity_periods.all():
                if activity_period.activity != activity:
                    return False
        return True
