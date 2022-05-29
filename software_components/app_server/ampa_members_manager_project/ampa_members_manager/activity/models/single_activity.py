from django.db import models
from django.utils.translation import gettext as _


class PaymentType(models.IntegerChoices):
    SINGLE = 1
    PER_DAY = 2


class SingleActivity(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    price_for_member = models.DecimalField(max_digits=6, decimal_places=2, verbose_name=_("Price for members"))
    price_for_no_member = models.DecimalField(max_digits=6, decimal_places=2, verbose_name=_("Price for no members"))
    payment_type = models.IntegerField(choices=PaymentType.choices, verbose_name=_("Payment type"))

    class Meta:
        verbose_name = _('Single activity')
        verbose_name_plural = _('Single activities')

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
