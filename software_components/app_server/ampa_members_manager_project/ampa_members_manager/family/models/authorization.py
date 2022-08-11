from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.family.models.bank_account import BankAccount

from gdstorage.storage import GoogleDriveStorage

gd_storage = GoogleDriveStorage()


class Authorization(models.Model):
    number = models.CharField(max_length=50, verbose_name=_("Number"))
    year = models.IntegerField(validators=[MinValueValidator(1000), MaxValueValidator(3000)], verbose_name=_("Year"))
    bank_account = models.OneToOneField(to=BankAccount, on_delete=CASCADE, verbose_name=_("Bank account"))
    document = models.FileField(null=True, blank=True, verbose_name=_("Document"), storage=gd_storage)

    class Meta:
        verbose_name = _('Authorization')
        verbose_name_plural = _("Authorizations")
        constraints = [
            models.UniqueConstraint(fields=['number', 'year'], name='unique_number_in_a_year')]

    def __str__(self) -> str:
        return f'{self.year}/{self.number}-{str(self.bank_account)}'
