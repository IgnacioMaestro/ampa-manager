from typing import Optional

from django.db import models
from django.db.models import CASCADE, Manager
from django.utils.translation import gettext_lazy as _

from ampa_manager.charge.models.fee.fee import Fee
from ampa_manager.charge.models.membership_receipt_queryset import MembershipReceiptQuerySet
from ampa_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_manager.charge.models.receipt_exceptions import NoBankAccountException, NoFeeForCourseException
from ampa_manager.charge.receipt import Receipt, AuthorizationReceipt
from ampa_manager.charge.state import State
from ampa_manager.family.models.authorization.authorization import Authorization
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.family import Family


class MembershipReceipt(models.Model):
    state = models.IntegerField(choices=State.choices, default=State.CREATED, verbose_name=_("State"))
    remittance = models.ForeignKey(to=MembershipRemittance, on_delete=CASCADE, verbose_name=_("Membership Remittance"))
    family = models.ForeignKey(to=Family, on_delete=CASCADE, verbose_name=_("Family"))

    objects = Manager.from_queryset(MembershipReceiptQuerySet)()

    class Meta:
        verbose_name = _('Membership receipt')
        verbose_name_plural = _('Membership receipts')
        db_table = 'membership_receipt'

    def generate_receipt(self) -> Receipt:
        bank_account: Optional[BankAccount] = self.family.default_bank_account
        if bank_account is None:
            raise NoBankAccountException
        try:
            fee: Fee = Fee.objects.get(academic_course=self.remittance.course)
        except Fee.DoesNotExist:
            raise NoFeeForCourseException
        bank_account_owner = str(bank_account.owner)
        iban: str = bank_account.iban
        authorization: AuthorizationReceipt = Authorization.generate_receipt_authorization(bank_account=bank_account)
        return Receipt(amount=fee.amount, bank_account_owner=bank_account_owner, iban=iban, authorization=authorization)
