from django.utils.translation import gettext_lazy as _

from django.db import models


class PricePerLevel(models.Model):
    levels = models.CharField(max_length=300, verbose_name=_("Levels"))
    price_for_member = models.DecimalField(max_digits=6, decimal_places=2, verbose_name=_("Price for members"))
    price_for_no_member = models.DecimalField(max_digits=6, decimal_places=2, verbose_name=_("Price for no members"))

    class Meta:
        abstract = True
