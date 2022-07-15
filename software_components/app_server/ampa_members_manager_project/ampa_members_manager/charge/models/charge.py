from __future__ import annotations

from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.activity_registration.models.activity_registration import ActivityRegistration
from ampa_members_manager.charge.models.charge_group import ChargeGroup
from ampa_members_manager.charge.state import State
from ampa_members_manager.charge.receipt import Receipt
from ampa_members_manager.family.models.authorization import Authorization
from ampa_members_manager.family.models.bank_account import BankAccount


class NotFound(Exception):
    pass


class Charge(models.Model):
    amount = models.FloatField(null=True, blank=True, verbose_name=_("Amount"))
    state = models.IntegerField(choices=State.choices, default=State.CREATED, verbose_name=_("State"))
    activity_registrations = models.ManyToManyField(to=ActivityRegistration, verbose_name=_("Activity registrations"))
    group = models.ForeignKey(to=ChargeGroup, on_delete=CASCADE, verbose_name=_("Group"))

    class Meta:
        verbose_name = _('Charge')
        verbose_name_plural = _('Charges')

    def check_bank_account(self, bank_account: BankAccount) -> bool:
        for activity_registration in self.activity_registrations.all():
            if activity_registration.bank_account == bank_account:
                return True
        return False

    def generate_receipt(self) -> Receipt:
        activity_registration: ActivityRegistration = self.activity_registrations.first()
        bank_account: BankAccount = activity_registration.bank_account
        try:
            authorization: Authorization = Authorization.objects.get(bank_account=bank_account)
            return Receipt(
                amount=self.amount, bank_account_owner=str(bank_account.owner),
                iban=bank_account.iban, authorization=str(authorization))
        except Authorization.DoesNotExist:
            return Receipt(
                amount=self.amount, bank_account_owner=str(bank_account.owner),
                iban=bank_account.iban, authorization='No authorization')

    @classmethod
    def find_charge_with_bank_account(cls, charge_group: ChargeGroup, bank_account: BankAccount) -> Charge:
        for charge in Charge.objects.filter(group=charge_group):
            if charge.check_bank_account(bank_account=bank_account):
                return charge
        raise NotFound
