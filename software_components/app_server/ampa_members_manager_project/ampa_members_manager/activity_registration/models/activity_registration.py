from __future__ import annotations

from django.db import models
from django.db.models import CASCADE, QuerySet
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.activity.models.single_activity import SingleActivity
from ampa_members_manager.family.models.bank_account import BankAccount
from ampa_members_manager.family.models.child import Child
from ampa_members_manager.family.models.membership import Membership


class ActivityRegistration(models.Model):
    amount = models.FloatField(default=0.0, verbose_name=_("Amount"))
    single_activity = models.ForeignKey(to=SingleActivity, on_delete=CASCADE, verbose_name=_("Single activity"))
    bank_account = models.ForeignKey(to=BankAccount, on_delete=CASCADE, verbose_name=_("Bank account"))
    child = models.ForeignKey(to=Child, on_delete=CASCADE, verbose_name=_("Child"))

    class Meta:
        verbose_name = _('Activity registration')
        verbose_name_plural = _("Activity registrations")

    def __str__(self) -> str:
        return f'{str(self.single_activity)}-{str(self.child)}'

    def calculate_price(self) -> float:
        return self.single_activity.calculate_price(times=self.amount, membership=self.is_membership())

    def establish_amount(self, amount) -> None:
        self.amount = amount
        self.save()

    def is_membership(self) -> bool:
        return Membership.is_membership_child(self.child)

    @classmethod
    def with_single_activity(cls, single_activity: SingleActivity) -> QuerySet[ActivityRegistration]:
        return ActivityRegistration.objects.filter(single_activity=single_activity)
