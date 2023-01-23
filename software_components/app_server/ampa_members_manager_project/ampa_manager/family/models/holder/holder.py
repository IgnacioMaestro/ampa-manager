import datetime

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _

from .holder_manager import HolderManager
from .holder_queryset import HolderQuerySet
from ..bank_account.bank_account import BankAccount
from ..parent import Parent
from ..state import State


class Holder(models.Model):
    parent = models.ForeignKey(to=Parent, on_delete=CASCADE, verbose_name=_("Holder"))
    bank_account = models.ForeignKey(to=BankAccount, on_delete=CASCADE, verbose_name=_("Bank Account"))
    authorization_order = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(999)], verbose_name=_("Order"))
    year = models.IntegerField(
        validators=[MinValueValidator(1000), MaxValueValidator(3000)], default=datetime.date.today().year,
        verbose_name=_("Year"))
    state = models.IntegerField(choices=State.choices, default=State.NOT_SENT, verbose_name=_("State"))
    sign_date = models.DateField(default=datetime.date.today)
    document = models.FileField(null=True, blank=True, upload_to='authorizations/', verbose_name=_("Document"))

    objects = HolderManager.from_queryset(HolderQuerySet)()

    class Meta:
        verbose_name = _('Holder')
        verbose_name_plural = _("Holders")
        db_table = 'holder'
        constraints = [
            models.UniqueConstraint(fields=['parent', 'bank_account'], name='unique_parent_and_bank_account'),
            models.UniqueConstraint(fields=['authorization_order', 'year'], name='unique_authorization_order_in_a_year')
        ]

    def __str__(self) -> str:
        return f'{self.parent}-{self.bank_account}'

    def clean(self):
        if self.state == State.SIGNED and not self.document:
            raise ValidationError(_('The state can not be sent or signed if there is no document attached'))

    @property
    def full_number(self) -> str:
        return f'{self.year}/{self.authorization_order:03}'
