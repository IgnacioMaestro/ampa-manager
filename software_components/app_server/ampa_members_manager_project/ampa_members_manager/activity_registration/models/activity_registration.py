from __future__ import annotations
from django.db import models
from django.db.models import CASCADE, SET_NULL, QuerySet

from ampa_members_manager.activity.models.single_activity import SingleActivity
from ampa_members_manager.activity_registration.models.payment_order import PaymentOrder
from ampa_members_manager.family.models.bank_account import BankAccount
from ampa_members_manager.family.models.child import Child
from ampa_members_manager.family.models.family import Family
from ampa_members_manager.family.models.membership import Membership


class ActivityRegistration(models.Model):
    amount = models.FloatField(default=0.0)
    single_activity = models.ForeignKey(to=SingleActivity, on_delete=CASCADE)
    bank_account = models.ForeignKey(to=BankAccount, on_delete=SET_NULL, null=True)
    registered_family = models.ForeignKey(to=Family, on_delete=CASCADE, null=True, blank=True)
    registered_child = models.ForeignKey(to=Child, on_delete=CASCADE, null=True, blank=True)
    payment_order = models.ForeignKey(to=PaymentOrder, on_delete=SET_NULL, null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="only one registered",
                check=(
                        models.Q(registered_family__isnull=False, registered_child__isnull=True) |
                        models.Q(registered_family__isnull=True, registered_child__isnull=False)
                ),
            )
        ]

    def __str__(self) -> str:
        registered_str = ''
        if self.registered_family is not None:
            registered_str = str(self.registered_family)
        if self.registered_child is not None:
            registered_str = str(self.registered_child)
        return f'{str(self.single_activity)}-{registered_str}'

    def establish_amount(self, amount) -> None:
        self.amount = amount
        self.save()

    def set_payment_order(self, amount: float):
        self.payment_order = PaymentOrder.objects.create(amount=amount)
        self.save()

    def is_membership(self) -> bool:
        if self.registered_family is not None:
            return Membership.is_membership_family(self.registered_family)
        if self.registered_child is not None:
            return Membership.is_membership_child(self.registered_child)

    @classmethod
    def with_single_activity(cls, single_activity: SingleActivity) -> QuerySet[ActivityRegistration]:
        return ActivityRegistration.objects.filter(single_activity=single_activity)
