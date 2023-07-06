from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.activity.models.custody.custody_registration_queryset import CustodyRegistrationQuerySet
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.membership import Membership


class CustodyRegistration(models.Model):
    custody_edition = models.ForeignKey(to=CustodyEdition, on_delete=models.CASCADE, verbose_name=_("Custody edition"))
    child = models.ForeignKey(to=Child, on_delete=models.CASCADE, verbose_name=_("Child"))
    holder = models.ForeignKey(to=Holder, on_delete=models.CASCADE, verbose_name=_("Holder"))
    assisted_days = models.PositiveIntegerField()

    objects = Manager.from_queryset(CustodyRegistrationQuerySet)()

    class Meta:
        verbose_name = _('Custody registration')
        verbose_name_plural = _('Custody registrations')
        db_table = 'custody_registration'
        constraints = [
            models.UniqueConstraint(fields=['custody_edition', 'child'], name='unique_custody_edition_for_child'),
        ]

    def __str__(self):
        return f'{self.custody_edition}, {self.child}'

    def clean(self):
        if self.holder and not self.holder.parent.family_set.filter(id=self.child.family.id).exists():
            raise ValidationError(_('The selected bank account does not belong to the child\'s family'))

    def calculate_price(self) -> float:
        assisted_days_for_charge: int = min([self.assisted_days, self.custody_edition.max_days_for_charge])
        if self.is_member:
            return float(assisted_days_for_charge) * float(self.custody_edition.price_for_member)
        else:
            return float(assisted_days_for_charge) * float(self.custody_edition.price_for_no_member)

    @property
    def is_member(self):
        return Membership.is_member_child(self.child)
