from django.db import models
from django.db.models import CASCADE
from localflavor.generic.models import IBANField, BICField

from ampa_members_manager.family.models.parent import Parent


class BankAccount(models.Model):
    swift_bic = BICField()
    iban = IBANField()
    owner = models.ForeignKey(to=Parent, on_delete=CASCADE)

    def __str__(self) -> str:
        return f'{self.iban}'
