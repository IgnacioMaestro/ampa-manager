from __future__ import annotations
from django.db import models
from django.db.models import Q, CASCADE, QuerySet
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.activity.models.repetitive_activity import RepetitiveActivity
from ampa_members_manager.activity.models.unique_activity import UniqueActivity


class PaymentType(models.IntegerChoices):
    SINGLE = 1
    PER_DAY = 2
    PER_WEEK = 3
    PER_MONTH = 4


class SingleActivity(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    price_for_member = models.DecimalField(max_digits=6, decimal_places=2, verbose_name=_("Price for members"))
    price_for_no_member = models.DecimalField(max_digits=6, decimal_places=2, verbose_name=_("Price for no members"))
    payment_type = models.IntegerField(choices=PaymentType.choices, verbose_name=_("Payment type"))
    repetitive_activity = models.ForeignKey(
        to=RepetitiveActivity, on_delete=CASCADE, null=True, blank=True, verbose_name=_("Repetitive Activity"))
    unique_activity = models.OneToOneField(
        to=UniqueActivity, on_delete=CASCADE, null=True, blank=True, verbose_name=_("Unique activity"))

    class Meta:
        verbose_name = _('Single activity')
        verbose_name_plural = _('Single activities')
        constraints = [
            models.CheckConstraint(
                check=(Q(repetitive_activity__isnull=False) & Q(unique_activity__isnull=True)
                       ) | (Q(repetitive_activity__isnull=True) & Q(unique_activity__isnull=False)),
                name='one_activity_reference'),
        ]

    def __str__(self) -> str:
        return f'{self.name}'

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
    def all_same_repetitive_activity(cls, single_activities: QuerySet[SingleActivity]) -> bool:
        if single_activities.count() > 1:
            if not SingleActivity.no_unique_activity(single_activities):
                return False
            repetitive_activity: RepetitiveActivity = single_activities.first().repetitive_activity
            single_activity: SingleActivity
            for single_activity in single_activities.all():
                if single_activity.repetitive_activity != repetitive_activity:
                    return False
        return True

    @classmethod
    def no_unique_activity(cls, single_activities: QuerySet[SingleActivity]) -> bool:
        for single_activity in single_activities.all():
            if single_activity.unique_activity is not None:
                return False
        return True
