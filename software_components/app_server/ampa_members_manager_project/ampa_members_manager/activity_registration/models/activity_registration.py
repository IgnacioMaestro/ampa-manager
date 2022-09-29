from __future__ import annotations

from django.db import models
from django.db.models import CASCADE, QuerySet
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from ampa_members_manager.activity.models.activity_period import ActivityPeriod
from ampa_members_manager.family.models.bank_account import BankAccount
from ampa_members_manager.family.models.child import Child
from ampa_members_manager.family.models.membership import Membership


class ActivityRegistration(models.Model):
    amount = models.FloatField(default=0.0, verbose_name=_("Amount"))
    activity_period = models.ForeignKey(to=ActivityPeriod, on_delete=CASCADE, verbose_name=_("Activity period"))
    bank_account = models.ForeignKey(to=BankAccount, on_delete=CASCADE, verbose_name=_("Bank account"))
    child = models.ForeignKey(to=Child, on_delete=CASCADE, verbose_name=_("Child"))

    class Meta:
        verbose_name = _('Activity registration')
        verbose_name_plural = _("Activity registrations")

    def __str__(self) -> str:
        return f'{str(self.activity_period)} - {str(self.child)}'

    def calculate_price(self) -> float:
        return self.activity_period.calculate_price(times=self.amount, membership=self.is_membership())

    def establish_amount(self, amount) -> None:
        self.amount = amount
        self.save()

    def is_membership(self) -> bool:
        return Membership.is_membership_child(self.child)

    @classmethod
    def with_activity_period(cls, activity_period: ActivityPeriod) -> QuerySet[ActivityRegistration]:
        return ActivityRegistration.objects.filter(activity_period=activity_period)
    
    def clean(self):
        if not self.bank_account.owner.family_set.filter(id=self.child.family.id).exists():
            raise ValidationError(_('The selected bank account does not belong to the child\'s family'))
