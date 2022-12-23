import datetime
from typing import Tuple, Optional

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import CASCADE
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.charge.receipt import Receipt, AuthorizationReceipt
from ampa_members_manager.family.models.authorization.authorization_manager import AuthorizationManager
from ampa_members_manager.family.models.authorization.authorization_queryset import AuthorizationQueryset
from ampa_members_manager.family.models.bank_account.bank_account import BankAccount
from ampa_members_manager.family.models.state import State


class Authorization(models.Model):
    number = models.CharField(max_length=50, verbose_name=_("Number"))
    order = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(999)], verbose_name=_("Order"))
    year = models.IntegerField(validators=[MinValueValidator(1000), MaxValueValidator(3000)], verbose_name=_("Year"))
    date = models.DateField(default=timezone.now().date)
    document = models.FileField(null=True, blank=True, upload_to='authorizations/', verbose_name=_("Document"))
    state = models.IntegerField(choices=State.choices, default=State.NOT_SENT, verbose_name=_("State"))
    bank_account = models.OneToOneField(to=BankAccount, on_delete=CASCADE, verbose_name=_("Bank account"))

    objects = AuthorizationManager.from_queryset(AuthorizationQueryset)()

    class Meta:
        verbose_name = _('Authorization')
        verbose_name_plural = _("Authorizations")
        constraints = [
            models.UniqueConstraint(fields=['number', 'year'], name='unique_number_in_a_year')]

    def __str__(self) -> str:
        return self.full_number + f'-{str(self.bank_account)}'

    def clean(self):
        if self.state == State.SIGNED and not self.document:
            raise ValidationError(_('The state can not be sent or signed if there is no document attached'))

    @property
    def full_number(self) -> str:
        return f'{self.year}/{self.order:03}'

    @classmethod
    def generate_receipt_authorization(cls, bank_account: BankAccount) -> Optional[AuthorizationReceipt]:
        try:
            authorization: Authorization = Authorization.objects.of_bank_account(bank_account).get()
            return AuthorizationReceipt(number=authorization.full_number, date=authorization.date)
        except Authorization.DoesNotExist:
            return None
