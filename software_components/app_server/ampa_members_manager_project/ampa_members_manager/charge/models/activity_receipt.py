from __future__ import annotations

from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.activity_registration.models.activity_registration import ActivityRegistration
from ampa_members_manager.charge.models.activity_remittance import ActivityRemittance
from ampa_members_manager.charge.state import State
from ampa_members_manager.charge.receipt import Receipt
from ampa_members_manager.family.models.authorization import Authorization
from ampa_members_manager.family.models.bank_account import BankAccount


class NotFound(Exception):
    pass


class ActivityReceipt(models.Model):
    amount = models.FloatField(null=True, blank=True, verbose_name=_("Total (€)"))
    state = models.IntegerField(choices=State.choices, default=State.CREATED, verbose_name=_("State"))
    activity_registrations = models.ManyToManyField(to=ActivityRegistration, verbose_name=_("Activity registrations"))
    remittance = models.ForeignKey(to=ActivityRemittance, on_delete=CASCADE, verbose_name=_("Activity remittance"))

    class Meta:
        verbose_name = _('Activity Receipt')
        verbose_name_plural = _('Activity Receipts')

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
                amount=str(self.amount), 
                bank_account_owner=str(bank_account.owner),
                iban=bank_account.iban, 
                authorization_number=str(authorization.number),
                authorization_date=authorization.date.strftime("%m/%d/%Y"))
        except Authorization.DoesNotExist:
            return Receipt(
                amount=str(self.amount), 
                bank_account_owner=str(bank_account.owner),
                iban=bank_account.iban, 
                authorization_number=str(Receipt.NO_AUTHORIZATION_MESSAGE),
                authorization_date='')

    @classmethod
    def find_activity_receipt_with_bank_account(
            cls, activity_remittance: ActivityRemittance, bank_account: BankAccount) -> ActivityReceipt:
        for activity_receipt in ActivityReceipt.objects.filter(remittance=activity_remittance):
            if activity_receipt.check_bank_account(bank_account=bank_account):
                return activity_receipt
        raise NotFound
