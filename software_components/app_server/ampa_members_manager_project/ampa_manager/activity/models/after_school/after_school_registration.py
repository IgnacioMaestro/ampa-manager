from django.db.models import Manager
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db import models

from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.activity.models.after_school.after_school_registration_queryset import \
    AfterSchoolRegistrationQuerySet
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.membership import Membership


class AfterSchoolRegistration(models.Model):
    after_school_edition = models.ForeignKey(
        to=AfterSchoolEdition, on_delete=models.CASCADE, verbose_name=_("After-school edition"))
    child = models.ForeignKey(to=Child, on_delete=models.CASCADE, verbose_name=_("Child"))
    bank_account = models.ForeignKey(to=BankAccount, on_delete=models.CASCADE, verbose_name=_("Bank account"))

    objects = Manager.from_queryset(AfterSchoolRegistrationQuerySet)()

    class Meta:
        verbose_name = _('After-school registration')
        verbose_name_plural = _('After-school registrations')
        db_table = 'after_school_registration'
        constraints = [
            models.UniqueConstraint(
                fields=['after_school_edition', 'child'], name='unique_after_school_edition_for_child'),
        ]

    def __str__(self) -> str:
        return f'{self.after_school_edition} {self.child}'

    def clean(self):
        if not self.bank_account.owner.family_set.filter(id=self.child.family.id).exists():
            raise ValidationError(_('The selected bank account does not belong to the child\'s family'))

    def calculate_price(self) -> float:
        if Membership.is_member_child(self.child):
            return float(self.after_school_edition.price_for_member)
        else:
            return float(self.after_school_edition.price_for_no_member)

    @staticmethod
    def find(after_school_edition, child):
        try:
            return AfterSchoolRegistration.objects.get(after_school_edition=after_school_edition, child=child)
        except AfterSchoolRegistration.DoesNotExist:
            return None
