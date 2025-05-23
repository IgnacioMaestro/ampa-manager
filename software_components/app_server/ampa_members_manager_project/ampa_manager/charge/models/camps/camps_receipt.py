from django.db import models
from django.db.models import CASCADE, Manager
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.camps.camps_registration import CampsRegistration
from ampa_manager.charge.receipt import Receipt, AuthorizationReceipt
from ampa_manager.family.models.holder.holder import Holder
from .camps_receipt_queryset import CampsReceiptQuerySet
from .camps_remittance import CampsRemittance
from ..receipt_exceptions import NoSwiftBicException


class CampsReceipt(models.Model):
    amount = models.FloatField(verbose_name=_("Total (€)"))
    camps_registration = models.ForeignKey(
        to=CampsRegistration, on_delete=CASCADE, verbose_name=_("Camps registrations"))
    remittance = models.ForeignKey(
        to=CampsRemittance, on_delete=CASCADE, verbose_name=_("Camps remittance"), related_name='receipts')

    objects = Manager.from_queryset(CampsReceiptQuerySet)()

    class Meta:
        verbose_name = _('Camps receipt')
        verbose_name_plural = _('Camps receipts')
        db_table = 'camps_receipt'

    def __str__(self):
        return f'{self.camps_registration}, {self.amount}'

    def generate_receipt(self) -> Receipt:
        holder: Holder = self.camps_registration.holder
        authorization: AuthorizationReceipt = AuthorizationReceipt(
            number=holder.authorization_full_number, date=holder.authorization_sign_date)
        if not holder.bank_account.swift_bic:
            raise NoSwiftBicException
        return Receipt(
            amount=self.amount, bank_account_owner=holder.parent.full_name, iban=holder.bank_account.iban,
            bic=holder.bank_account.swift_bic, authorization=authorization)

    @classmethod
    def get_total_by_remittance(cls, remittance: CampsRemittance) -> float:
        total = 0.0
        for receipt in CampsReceipt.objects.filter(remittance=remittance):
            total += receipt.amount
        return total
