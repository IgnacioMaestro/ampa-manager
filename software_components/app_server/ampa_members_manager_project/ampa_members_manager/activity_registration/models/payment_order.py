from django.db import models
from django.utils.translation import gettext as _


class PaymentOrder(models.Model):
    amount = models.FloatField(verbose_name=_("Amount"))

    class Meta:
        verbose_name = _('Payment order')
        verbose_name_plural = _('Payment orders')
