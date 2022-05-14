from __future__ import annotations
from django.db import models
from django.db.models import SET_NULL, QuerySet

from ampa_members_manager.family.models.bank_account import BankAccount
from ampa_members_manager.family.models.parent import Parent


class Family(models.Model):
    first_surname = models.CharField(max_length=500)
    second_surname = models.CharField(max_length=500)
    email = models.EmailField(unique=True)
    parents = models.ManyToManyField(to=Parent)
    default_bank_account = models.ForeignKey(to=BankAccount, on_delete=SET_NULL, null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.first_surname} {self.second_surname}'

    @classmethod
    def all_families(cls) -> QuerySet[Family]:
        return Family.objects.all()

    @classmethod
    def all_families_with_bank_account(cls) -> QuerySet[Family]:
        return cls.all_families().exclude(default_bank_account__isnull=True)
