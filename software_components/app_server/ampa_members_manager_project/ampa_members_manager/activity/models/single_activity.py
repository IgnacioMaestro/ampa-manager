from django.db import models
from django.utils.translation import gettext as _


class PaymentType(models.IntegerChoices):
    SINGLE = 1
    PER_DAY = 2


class SingleActivity(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=100)
    price_for_member = models.DecimalField(verbose_name=_("Price for members"), max_digits=6, decimal_places=2)
    price_for_no_member = models.DecimalField(verbose_name=_("Price for no members"), max_digits=6, decimal_places=2)
    payment_type = models.IntegerField(verbose_name=_("Payment type"), choices=PaymentType.choices)

    def __str__(self) -> str:
        return f'{self.name}'

    def calculate_price(self, times: float, membership: bool) -> float:
        if self.payment_type is PaymentType.SINGLE:
            if membership:
                return float(self.price_for_member)
            else:
                return float(self.price_for_no_member)
        else:
            if membership:
                return float(self.price_for_member) * times
            else:
                return float(self.price_for_no_member) * times
