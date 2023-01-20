from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _

from ..authorization.authorization import Authorization
from ..bank_account.bank_account import BankAccount
from ..parent import Parent


class Holder(Authorization):
    parent = models.ForeignKey(to=Parent, on_delete=CASCADE, verbose_name=_("Holder"))
    bank_account = models.ForeignKey(to=BankAccount, on_delete=CASCADE, verbose_name=_("Bank Account"))

    class Meta:
        verbose_name = _('Holder')
        verbose_name_plural = _("Holders")
        db_table = 'holder'
        constraints = Authorization.Meta.constraints + [
            models.UniqueConstraint(fields=['parent', 'bank_account'], name='%(class)s_unique_parent_and_bank_account')]

    def __str__(self) -> str:
        return f'{self.parent}-{self.bank_account}'
