from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.charge.models.custody.custody_remittance import CustodyRemittance
from ampa_manager.charge.receipt import Receipt, AuthorizationReceipt
from ampa_manager.charge.state import State
from ampa_manager.family.models.holder.holder import Holder


class CustodyReceipt(models.Model):
    amount = models.FloatField(verbose_name=_("Total (€)"))
    state = models.IntegerField(choices=State.choices, default=State.CREATED, verbose_name=_("State"))
    custody_registration = models.ForeignKey(
        to=CustodyRegistration, on_delete=CASCADE, verbose_name=_("Custody registrations"))
    remittance = models.ForeignKey(
        to=CustodyRemittance, on_delete=CASCADE, verbose_name=_("Custody remittance"))

    class Meta:
        verbose_name = _('Custody receipt')
        verbose_name_plural = _('Custody receipts')
        db_table = 'custody_receipt'

    def generate_receipt(self) -> Receipt:
        holder: Holder = self.custody_registration.holder
        authorization: AuthorizationReceipt = AuthorizationReceipt(
            number=holder.authorization_full_number, date=holder.authorization_sign_date)
        return Receipt(
            amount=self.amount, bank_account_owner=str(holder.parent), iban=holder.bank_account.iban,
            bic=holder.bank_account.swift_bic, authorization=authorization)