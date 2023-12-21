from typing import Optional

from django.db import models
from django.db.models import CASCADE, Manager
from django.utils.translation import gettext_lazy as _

from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder
from .fee.fee import Fee
from .membership_receipt_queryset import MembershipReceiptQuerySet
from .membership_remittance import MembershipRemittance
from .receipt_exceptions import NoFeeForCourseException, NoHolderException
from ..receipt import Receipt, AuthorizationReceipt
from ..state import State


class MembershipReceipt(models.Model):
    state = models.IntegerField(choices=State.choices, default=State.CREATED, verbose_name=_("State"))
    remittance = models.ForeignKey(to=MembershipRemittance, on_delete=CASCADE, verbose_name=_("Membership Remittance"))
    family = models.ForeignKey(to=Family, on_delete=CASCADE, verbose_name=_("Family"))

    objects = Manager.from_queryset(MembershipReceiptQuerySet)()

    class Meta:
        verbose_name = _('Membership receipt')
        verbose_name_plural = _('Membership receipts')
        db_table = 'membership_receipt'

    def __str__(self) -> str:
        return f'{self.remittance} {self.family}'

    def generate_receipt(self) -> Receipt:
        holder: Optional[Holder] = self.family.default_holder
        if holder is None:
            raise NoHolderException
        try:
            fee: Fee = Fee.objects.get(academic_course=self.remittance.course)
        except Fee.DoesNotExist:
            raise NoFeeForCourseException
        bank_account_owner = holder.parent.full_name
        iban: str = holder.bank_account.iban
        bic: str = holder.bank_account.swift_bic
        authorization: AuthorizationReceipt = MembershipReceipt.generate_authorization_receipt_from_holder(holder)
        return Receipt(
            amount=fee.amount, bank_account_owner=bank_account_owner, iban=iban, bic=bic, authorization=authorization)

    @classmethod
    def generate_authorization_receipt_from_holder(cls, holder: Holder) -> AuthorizationReceipt:
        return AuthorizationReceipt(number=holder.authorization_full_number, date=holder.authorization_sign_date)
