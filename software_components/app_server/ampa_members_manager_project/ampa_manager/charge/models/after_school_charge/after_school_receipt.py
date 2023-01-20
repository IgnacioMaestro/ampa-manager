from typing import Optional

from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.family.models.authorization.authorization_old import AuthorizationOld
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from .after_school_remittance import AfterSchoolRemittance
from ...receipt import Receipt, AuthorizationReceipt
from ...state import State


class AfterSchoolReceipt(models.Model):
    amount = models.FloatField(verbose_name=_("Total (€)"))
    state = models.IntegerField(choices=State.choices, default=State.CREATED, verbose_name=_("State"))
    after_school_registration = models.ForeignKey(
        to=AfterSchoolRegistration, on_delete=CASCADE, verbose_name=_("After School registrations"))
    remittance = models.ForeignKey(
        to=AfterSchoolRemittance, on_delete=CASCADE, verbose_name=_("After School remittance"))

    class Meta:
        verbose_name = _('After-school receipt')
        verbose_name_plural = _('After-school receipts')
        db_table = 'after_school_receipt'

    def generate_receipt(self) -> Receipt:
        bank_account: BankAccount = self.after_school_registration.bank_account
        authorization: Optional[AuthorizationReceipt] = AuthorizationOld.generate_receipt_authorization(
            bank_account=bank_account)
        return Receipt(
            amount=self.amount, bank_account_owner=str(bank_account.owner), iban=bank_account.iban,
            bic=bank_account.swift_bic, authorization=authorization)
