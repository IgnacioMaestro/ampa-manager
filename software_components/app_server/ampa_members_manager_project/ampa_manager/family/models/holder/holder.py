import datetime

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _

from ampa_manager.utils.utils import Utils
from .holder_manager import HolderManager
from .holder_queryset import HolderQuerySet
from ..bank_account.bank_account import BankAccount
from ..parent import Parent
from ..state import State


def generate_holder_authorization_file_name(instance, filename):
    path = 'authorizations/'
    extension = filename.split('.')[-1]
    filename = f'{instance.authorization_year}_{instance.authorization_order}'
    return f'{path}{filename}.{extension}'


class Holder(models.Model):
    parent = models.ForeignKey(to=Parent, on_delete=CASCADE, verbose_name=_("Holder"))
    bank_account = models.ForeignKey(to=BankAccount, on_delete=CASCADE, verbose_name=_("Bank Account"))
    authorization_order = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1999)], verbose_name=_("Order"))
    authorization_year = models.IntegerField(
        validators=[MinValueValidator(1000), MaxValueValidator(3000)], default=datetime.date.today().year,
        verbose_name=_("Year"))
    authorization_state = models.IntegerField(choices=State.choices, default=State.NOT_SENT, verbose_name=_("State"))
    authorization_sign_date = models.DateField(default=datetime.date.today)
    authorization_document = models.FileField(
        null=True, blank=True, upload_to=generate_holder_authorization_file_name, verbose_name=_("Document"))

    objects = HolderManager.from_queryset(HolderQuerySet)()

    class Meta:
        verbose_name = _('Holder')
        verbose_name_plural = _("Holders")
        db_table = 'holder'
        constraints = [
            models.UniqueConstraint(fields=['parent', 'bank_account'], name='unique_parent_and_bank_account'),
            models.UniqueConstraint(
                fields=['authorization_order', 'authorization_year'], name='unique_authorization_order_in_a_year')
        ]

    def __str__(self) -> str:
        return f'{self.parent}, {self.bank_account}'

    def clean(self):
        if self.authorization_state == State.SIGNED and not self.authorization_document:
            raise ValidationError(_('The state can not be sent or signed if there is no document attached'))

    def get_html_link(self, print_family_id=False) -> str:
        link_text = str(self)
        if print_family_id:
            families_ids = [str(f.id) for f in self.parent.family_set.all()]
            families_ids_csv = ', '.join(families_ids)
            link_text += f' (Family: {families_ids_csv})'

        return Utils.get_model_instance_link(Holder.__name__.lower(), self.id, link_text)

    @property
    def authorization_full_number(self) -> str:
        return f'{self.authorization_year}/{self.authorization_order:03}'

    @staticmethod
    def find(parent: Parent, bank_account: BankAccount):
        holders = Holder.objects.of_parent_and_bank_account(parent, bank_account)
        if holders.count() == 1:
            return holders.first()
        else:
            return None
