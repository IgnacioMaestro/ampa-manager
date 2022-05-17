from __future__ import annotations

from django.db import models
from django.db.models import CASCADE, SET_NULL, QuerySet
from django.utils.translation import gettext as _

from ampa_members_manager.activity.models.single_activity import SingleActivity
from ampa_members_manager.activity_registration.models.payment_order import PaymentOrder
from ampa_members_manager.family.models.bank_account import BankAccount
from ampa_members_manager.family.models.child import Child
from ampa_members_manager.family.models.membership import Membership


class ActivityRegistration(models.Model):
    amount = models.FloatField(verbose_name=_("Amount"), default=0.0)
    single_activity = models.ForeignKey(verbose_name=_("Single activity"), to=SingleActivity, on_delete=CASCADE)
    bank_account = models.ForeignKey(verbose_name=_("Bank account"), to=BankAccount, on_delete=SET_NULL, null=True)
    child = models.ForeignKey(verbose_name=_("Child"), to=Child, on_delete=CASCADE)
    payment_order = models.ForeignKey(verbose_name=_("Payment order"), to=PaymentOrder, on_delete=SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = _('Activity registration')
        verbose_name_plural = _('Activity registrations')

    def __str__(self) -> str:
        return f'{str(self.single_activity)}-{str(self.child)}'

    def establish_amount(self, amount) -> None:
        self.amount = amount
        self.save()

    def set_payment_order(self, amount: float):
        self.payment_order = PaymentOrder.objects.create(amount=amount)
        self.save()

    def is_membership(self) -> bool:
        return Membership.is_membership_child(self.child)

    @classmethod
    def with_single_activity(cls, single_activity: SingleActivity) -> QuerySet[ActivityRegistration]:
        return ActivityRegistration.objects.filter(single_activity=single_activity)
