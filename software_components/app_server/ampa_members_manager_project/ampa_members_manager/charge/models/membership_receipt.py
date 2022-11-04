from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_members_manager.charge.models.receipt_exceptions import NoBankAccountException, NoFeeForCourseException
from ampa_members_manager.charge.receipt import Receipt
from ampa_members_manager.charge.state import State
from ampa_members_manager.family.models.authorization.authorization import Authorization
from ampa_members_manager.family.models.bank_account.bank_account import BankAccount
from ampa_members_manager.family.models.family import Family


class MembershipReceipt(models.Model):
    state = models.IntegerField(choices=State.choices, default=State.CREATED, verbose_name=_("State"))
    remittance = models.ForeignKey(to=MembershipRemittance, on_delete=CASCADE, verbose_name=_("Membership Remittance"))
    family = models.ForeignKey(to=Family, on_delete=CASCADE, verbose_name=_("Family"))

    class Meta:
        verbose_name = _('Membership receipt')
        verbose_name_plural = _('Membership receipts')

    def generate_receipt(self) -> Receipt:
        if self.family.default_bank_account is None:
            raise NoBankAccountException
        if self.remittance.course.fee is None:
            raise NoFeeForCourseException
        bank_account_owner: str = str(self.family.default_bank_account.owner)
        iban: str = self.family.default_bank_account.iban
        amount = self.remittance.course.fee
        authorization_number, authorization_date = self.__obtain_authorization()
        return Receipt(amount, bank_account_owner, iban, authorization_number, authorization_date)

    def __obtain_authorization(self):
        try:
            bank_account: BankAccount = self.family.default_bank_account
            authorization: Authorization = Authorization.objects.of_bank_account(bank_account).get()
            authorization_number = authorization.number
            authorization_date = authorization.date
        except Authorization.DoesNotExist:
            authorization_number = Receipt.NO_AUTHORIZATION_MESSAGE
            authorization_date = None
        return authorization_number, authorization_date
