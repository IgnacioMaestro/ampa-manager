from django.db import models
from django.db.models import CASCADE, Manager
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.camps.camps_registration import CampsRegistration
from ampa_manager.charge.receipt import Receipt, AuthorizationReceipt
from ampa_manager.charge.state import State
from ampa_manager.family.models.holder.holder import Holder
from .camps_receipt_queryset import CampsReceiptQuerySet

from .camps_remittance import CampsRemittance


class CampsReceipt(models.Model):
    amount = models.FloatField(verbose_name=_("Total (€)"))
    state = models.IntegerField(choices=State.choices, default=State.CREATED, verbose_name=_("State"))
    camps_registration = models.ForeignKey(
        to=CampsRegistration, on_delete=CASCADE, verbose_name=_("Camps registrations"))
    remittance = models.ForeignKey(
        to=CampsRemittance, on_delete=CASCADE, verbose_name=_("Camps remittance"))

    objects = Manager.from_queryset(CampsReceiptQuerySet)()

    class Meta:
        verbose_name = _('Camps receipt')
        verbose_name_plural = _('Camps receipts')
        db_table = 'camps_receipt'

    def __str__(self):
        return f'{self.camps_registration}, {self.get_state_display()}, {self.amount}'

    def generate_receipt(self) -> Receipt:
        holder: Holder = self.camps_registration.holder
        authorization: AuthorizationReceipt = AuthorizationReceipt(
            number=holder.authorization_full_number, date=holder.authorization_sign_date)
        return Receipt(
            amount=self.amount, bank_account_owner=holder.parent.full_name, iban=holder.bank_account.iban,
            bic=holder.bank_account.swift_bic, authorization=authorization)
