from __future__ import annotations

from django.db import models
from django.db.models import CASCADE, QuerySet
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.activity.models.activity_payable_part import ActivityPayablePart
from ampa_members_manager.family.models.bank_account import BankAccount
from ampa_members_manager.family.models.child import Child
from ampa_members_manager.family.models.membership import Membership


class ActivityRegistration(models.Model):
    amount = models.FloatField(default=0.0, verbose_name=_("Amount"))
    payable_part = models.ForeignKey(to=ActivityPayablePart, on_delete=CASCADE, verbose_name=_("Activity Payable Part"))
    bank_account = models.ForeignKey(to=BankAccount, on_delete=CASCADE, verbose_name=_("Bank account"))
    child = models.ForeignKey(to=Child, on_delete=CASCADE, verbose_name=_("Child"))

    class Meta:
        verbose_name = _('Activity registration')
        verbose_name_plural = _("Activity registrations")

    def __str__(self) -> str:
        return f'{str(self.payable_part)}-{str(self.child)}'

    def calculate_price(self) -> float:
        return self.payable_part.calculate_price(times=self.amount, membership=self.is_membership())

    def establish_amount(self, amount) -> None:
        self.amount = amount
        self.save()

    def is_membership(self) -> bool:
        return Membership.is_membership_child(self.child)

    @classmethod
    def with_payable_part(cls, payable_part: ActivityPayablePart) -> QuerySet[ActivityRegistration]:
        return ActivityRegistration.objects.filter(payable_part=payable_part)
