from django.db import models
from django.db.models import CASCADE

from ampa_members_manager.family.models.parent import Parent


class BankAccount(models.Model):
    swift_bic = models.CharField(max_length=30)
    iban = models.CharField(max_length=30)
    owner = models.ForeignKey(to=Parent, on_delete=CASCADE)

    def __str__(self) -> str:
        return "{}".format(self.iban)
