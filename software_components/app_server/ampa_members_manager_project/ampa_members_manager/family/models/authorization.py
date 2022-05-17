from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import CASCADE

from ampa_members_manager.family.models.bank_account import BankAccount


class Authorization(models.Model):
    number = models.CharField(max_length=50)
    year = models.IntegerField(validators=[MinValueValidator(1000), MaxValueValidator(3000)])
    bank_account = models.OneToOneField(to=BankAccount, on_delete=CASCADE)
    document = models.FileField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['number', 'year'], name='unique_number_in_a_year')]

    def __str__(self) -> str:
        return f'{self.year}/{self.number}-{str(self.bank_account)}'
