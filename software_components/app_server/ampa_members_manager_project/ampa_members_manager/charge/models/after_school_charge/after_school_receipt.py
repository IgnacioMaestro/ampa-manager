from typing import Optional

from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_members_manager.charge.models.after_school_charge.after_school_remittance import AfterSchoolRemittance
from ampa_members_manager.charge.receipt import Receipt, AuthorizationReceipt
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
        db_table = 'after_school_receipt'

    def generate_receipt(self) -> Receipt:
        bank_account: BankAccount = self.after_school_registration.bank_account
        authorization: Optional[AuthorizationReceipt] = Authorization.generate_receipt_authorization(
            bank_account=bank_account)
        return Receipt(
            amount=self.amount, bank_account_owner=str(bank_account.owner), iban=bank_account.iban,
            authorization=authorization)
