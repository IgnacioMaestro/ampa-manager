from __future__ import annotations
from xmlrpc.client import Boolean
from django.db import models
from django.db.models import SET_NULL, QuerySet
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.family.models.bank_account import BankAccount
from ampa_members_manager.family.models.parent import Parent


class Family(models.Model):
    surnames = models.CharField(max_length=500, verbose_name=_("Surnames"))
    email = models.EmailField(unique=True, verbose_name=_("Email"))
    secondary_email = models.EmailField(null=True, blank=True, verbose_name=_("Secondary Email"))
    parents = models.ManyToManyField(to=Parent, verbose_name=_("Parents"))
    default_bank_account = models.ForeignKey(
        to=BankAccount, on_delete=SET_NULL, null=True, blank=True, verbose_name=_("Default bank account"),
        help_text=_("Save the family to see its bank accounts"))
    is_defaulter = models.BooleanField(default=False, verbose_name=_("Defaulter"))

    class Meta:
        verbose_name = _('Family')
        verbose_name_plural = _("Families")

    def __str__(self) -> str:
        return f'{self.surnames}'

    @classmethod
    def all_families(cls) -> QuerySet[Family]:
        return Family.objects.all()

    @classmethod
    def all_families_with_bank_account(cls) -> QuerySet[Family]:
        return cls.all_families().exclude(default_bank_account__isnull=True)
    