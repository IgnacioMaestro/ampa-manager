from django.db import models
from django.db.models import CASCADE, Manager
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from .after_school_receipt_queryset import AfterSchoolReceiptQuerySet
from .after_school_remittance import AfterSchoolRemittance
from ...receipt import Receipt


class AfterSchoolReceipt(models.Model):
    amount = models.FloatField(verbose_name=_("Total (€)"))
    after_school_registration = models.ForeignKey(
        to=AfterSchoolRegistration, on_delete=CASCADE, verbose_name=_("After School registrations"))
    remittance = models.ForeignKey(
        to=AfterSchoolRemittance, on_delete=CASCADE, verbose_name=_("After School remittance"), related_name='receipts')

    objects = Manager.from_queryset(AfterSchoolReceiptQuerySet)()

    class Meta:
        verbose_name = _('After-school receipt')
        verbose_name_plural = _('After-school receipts')
        db_table = 'after_school_receipt'

    def __str__(self):
        return f'{self.after_school_registration}, {self.amount}'

    def generate_receipt(self) -> Receipt:
        return self.after_school_registration.holder.generate_receipt_with(self.amount)

    @classmethod
    def get_total_by_remittance(cls, remittance: AfterSchoolRemittance) -> float:
        total = 0.0
        for receipt in AfterSchoolReceipt.objects.filter(remittance=remittance):
            total += receipt.amount
        return total
