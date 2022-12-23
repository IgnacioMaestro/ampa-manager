from typing import Optional

from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_members_manager.charge.models.after_school_charge.after_school_remittance import AfterSchoolRemittance
from ampa_members_manager.charge.receipt import Receipt
from ampa_members_manager.charge.state import State
from ampa_members_manager.family.models.authorization.authorization import Authorization
from ampa_members_manager.family.models.bank_account.bank_account import BankAccount


class AfterSchoolReceipt(models.Model):
    amount = models.FloatField(verbose_name=_("Total (€)"))
    state = models.IntegerField(choices=State.choices, default=State.CREATED, verbose_name=_("State"))
    after_school_registration = models.ForeignKey(
        to=AfterSchoolRegistration, on_delete=CASCADE, verbose_name=_("After School registrations"))
    remittance = models.ForeignKey(
        to=AfterSchoolRemittance, on_delete=CASCADE, verbose_name=_("After School remittance"))

    class Meta:
        verbose_name = _('After School Receipt')
        verbose_name_plural = _('After School Receipts')

    def generate_receipt(self) -> Receipt:
        bank_account: Optional[BankAccount] = self.after_school_registration.bank_account
        bank_account_owner: str = str(bank_account.owner)
        iban: str = bank_account.iban
        authorization_number, authorization_date = Authorization.generate_receipt_authorization(
            bank_account=bank_account)
        amount = self.after_school_registration.calculate_price()
        return Receipt(str(amount), bank_account_owner, iban, authorization_number, authorization_date)
