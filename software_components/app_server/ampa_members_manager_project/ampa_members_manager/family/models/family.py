from __future__ import annotations
from django.db import models
from django.db.models import SET_NULL, QuerySet
from django.utils.translation import gettext as _

from ampa_members_manager.family.models.bank_account import BankAccount
from ampa_members_manager.family.models.parent import Parent


class Family(models.Model):
    first_surname = models.CharField(verbose_name=_("First surname"), max_length=500)
    second_surname = models.CharField(verbose_name=_("Second surname"), max_length=500)
    email = models.EmailField(verbose_name=_("Email"), unique=True)
    parents = models.ManyToManyField(verbose_name=_("Parents"), to=Parent)
    default_bank_account = models.ForeignKey(verbose_name=_("Default bank account"), to=BankAccount, on_delete=SET_NULL, null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['first_surname', 'second_surname'], name='unique_surnames')]
        verbose_name = _('Family')
        verbose_name_plural = _('Families')

    def __str__(self) -> str:
        return f'{self.first_surname} {self.second_surname}'

    @classmethod
    def all_families(cls) -> QuerySet[Family]:
        return Family.objects.all()

    @classmethod
    def all_families_with_bank_account(cls) -> QuerySet[Family]:
        return cls.all_families().exclude(default_bank_account__isnull=True)
