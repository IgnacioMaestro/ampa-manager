from django.db import models


class PaymentType(models.IntegerChoices):
    SINGLE = 1
    PER_DAY = 2


class SingleActivity(models.Model):
    name = models.CharField(max_length=100)
    price_for_member = models.DecimalField(max_digits=6, decimal_places=2)
    price_for_no_member = models.DecimalField(max_digits=6, decimal_places=2)
    payment_type = models.IntegerField(choices=PaymentType.choices)

    def __str__(self) -> str:
        return f'{self.name}'
