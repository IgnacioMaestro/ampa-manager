from django.db import models
from django.db.models import CASCADE

from ampa_members_manager.family.models.bank_account import BankAccount


class Authorization(models.Model):
    number = models.CharField(max_length=50)
    date = models.DateField()
    bank_account = models.OneToOneField(to=BankAccount, on_delete=CASCADE)

    def __str__(self) -> str:
        return f'{self.number}-{str(self.bank_account)}'