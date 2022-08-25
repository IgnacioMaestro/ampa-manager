from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class PaymentType(models.IntegerChoices):
    SINGLE = (1, _('Single'))
    PER_DAY = (2, _('Per day'))
    PER_WEEK = (3, _('Per week'))
    PER_MONTH = (4, _('Per month'))
