from django.db.models import Manager
from django.utils.translation import gettext_lazy as _
from django.db import models

from ampa_members_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_members_manager.activity.models.after_school.after_school_registration_queryset import \
    AfterSchoolRegistrationQuerySet
from ampa_members_manager.family.models.bank_account.bank_account import BankAccount
from ampa_members_manager.family.models.child import Child
from ampa_members_manager.family.models.membership import Membership


class AfterSchoolRegistration(models.Model):
    after_school_edition = models.ForeignKey(
        to=AfterSchoolEdition, on_delete=models.CASCADE, verbose_name=_("AfterSchoolEdition"))
    child = models.ForeignKey(to=Child, on_delete=models.CASCADE, verbose_name=_("Child"))
    bank_account = models.ForeignKey(to=BankAccount, on_delete=models.CASCADE, verbose_name=_("BankAccount"))

    objects = Manager.from_queryset(AfterSchoolRegistrationQuerySet)()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['after_school_edition', 'child'], name='unique_after_school_edition_for_child'),
        ]

    def __str__(self) -> str:
        return f'{self.after_school_edition} {self.child}'

    def calculate_price(self) -> float:
        if Membership.is_member_child(self.child):
            return float(self.after_school_edition.price_for_member)
        else:
            return float(self.after_school_edition.price_for_no_member)
