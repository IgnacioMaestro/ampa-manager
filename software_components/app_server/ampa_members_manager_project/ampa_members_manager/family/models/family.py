from __future__ import annotations
from django.db import models
from django.db.models import SET_NULL, QuerySet, Manager
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.family.models.bank_account import BankAccount
from ampa_members_manager.family.models.parent import Parent
from ampa_members_manager.family.models.family_queryset import FamilyQuerySet


class Family(models.Model):
    surnames = models.CharField(max_length=500, verbose_name=_("Surnames"))
    email = models.EmailField(unique=True, verbose_name=_("Email"))
    secondary_email = models.EmailField(null=True, blank=True, verbose_name=_("Secondary Email"))
    parents = models.ManyToManyField(to=Parent, verbose_name=_("Parents"))
    default_bank_account = models.ForeignKey(
        to=BankAccount, on_delete=SET_NULL, null=True, blank=True, verbose_name=_("Default bank account"),
        help_text=_("Save the family to see its bank accounts"))
    is_defaulter = models.BooleanField(default=False, verbose_name=_("Defaulter"))

    objects = Manager.from_queryset(FamilyQuerySet)()

    class Meta:
        verbose_name = _('Family')
        verbose_name_plural = _("Families")

    def __str__(self) -> str:
        return f'{self.surnames}'
    
    @classmethod
    def all_families(cls) -> QuerySet[Family]:
        return Family.objects.all()

    def clean(self):
        if self.surnames:
            self.surnames = self.surnames.title().strip()
    