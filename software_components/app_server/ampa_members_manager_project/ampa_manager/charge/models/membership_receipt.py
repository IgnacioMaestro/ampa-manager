from typing import Optional

from django.db import models
from django.db.models import CASCADE, Manager
from django.utils.translation import gettext_lazy as _

from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder
from .fee.fee import Fee
from .membership_receipt_queryset import MembershipReceiptQuerySet
from .membership_remittance import MembershipRemittance
from .receipt_exceptions import NoFeeForCourseException, NoSwiftBicException
from ..receipt import Receipt, AuthorizationReceipt


class MembershipReceipt(models.Model):
    remittance = models.ForeignKey(to=MembershipRemittance, on_delete=CASCADE, verbose_name=_("Membership Remittance"))
    family = models.ForeignKey(to=Family, on_delete=CASCADE, verbose_name=_("Family"))
    holder = models.ForeignKey(to=Holder, on_delete=CASCADE, verbose_name=_("Holder"))

    objects = Manager.from_queryset(MembershipReceiptQuerySet)()

    class Meta:
        verbose_name = _('Membership receipt')
        verbose_name_plural = _('Membership receipts')
        db_table = 'membership_receipt'

    def __str__(self) -> str:
        return f'{self.remittance} {self.family}'

    def generate_receipt(self) -> Receipt:
        try:
            fee: Fee = Fee.objects.get(academic_course=self.remittance.course)
        except Fee.DoesNotExist:
            raise NoFeeForCourseException
        bank_account_owner = self.holder.parent.full_name
        iban: str = self.holder.bank_account.iban
        bic: Optional[str] = self.holder.bank_account.swift_bic
        if bic is None:
            raise NoSwiftBicException
        authorization: AuthorizationReceipt = MembershipReceipt.generate_authorization_receipt_from_holder(self.holder)
        return Receipt(
            amount=fee.amount, bank_account_owner=bank_account_owner, iban=iban, bic=bic, authorization=authorization)

    @classmethod
    def generate_authorization_receipt_from_holder(cls, holder: Holder) -> AuthorizationReceipt:
        return AuthorizationReceipt(number=holder.authorization_full_number, date=holder.authorization_sign_date)
