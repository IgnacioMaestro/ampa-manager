from django.db import models
from django.db.models import CASCADE, Manager
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.charge.models.custody.custody_receipt_queryset import CustodyReceiptQuerySet
from ampa_manager.charge.models.custody.custody_remittance import CustodyRemittance
from ampa_manager.charge.receipt import Receipt


class CustodyReceipt(models.Model):
    amount = models.FloatField(verbose_name=_("Total (€)"))
    custody_registration = models.ForeignKey(
        to=CustodyRegistration, on_delete=CASCADE, verbose_name=_("Custody registrations"))
    remittance = models.ForeignKey(
        to=CustodyRemittance, on_delete=CASCADE, verbose_name=_("Custody remittance"), related_name='receipts')

    objects = Manager.from_queryset(CustodyReceiptQuerySet)()

    class Meta:
        verbose_name = _('Custody receipt')
        verbose_name_plural = _('Custody receipts')
        db_table = 'custody_receipt'

    def __str__(self):
        return f'{self.custody_registration}, {self.amount}'

    def generate_receipt(self) -> Receipt:
        return self.custody_registration.holder.generate_receipt_with(self.amount)

    @classmethod
    def get_total_by_remittance(cls, remittance: CustodyRemittance) -> float:
        total = 0.0
        for receipt in CustodyReceipt.objects.filter(remittance=remittance):
            total += receipt.amount
        return total
