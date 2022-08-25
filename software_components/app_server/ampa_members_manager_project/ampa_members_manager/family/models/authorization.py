from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.family.models.bank_account import BankAccount
from ampa_members_manager.charge.state import State


class Authorization(models.Model):
    number = models.CharField(max_length=50, verbose_name=_("Number"))
    year = models.IntegerField(validators=[MinValueValidator(1000), MaxValueValidator(3000)], verbose_name=_("Year"))
    bank_account = models.OneToOneField(to=BankAccount, on_delete=CASCADE, verbose_name=_("Bank account"))
    document = models.FileField(null=True, blank=True, upload_to='authorizations/', verbose_name=_("Document"))
    state = models.IntegerField(choices=State.choices, default=State.CREATED, verbose_name=_("State"))

    class Meta:
        verbose_name = _('Authorization')
        verbose_name_plural = _("Authorizations")
        constraints = [
            models.UniqueConstraint(fields=['number', 'year'], name='unique_number_in_a_year')]

    def __str__(self) -> str:
        return f'{self.year}/{self.number}-{str(self.bank_account)}'
