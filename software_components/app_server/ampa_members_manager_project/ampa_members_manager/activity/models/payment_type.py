from __future__ import annotations

from django.db import models


class PaymentType(models.IntegerChoices):
    SINGLE = 1
    PER_DAY = 2
    PER_WEEK = 3
    PER_MONTH = 4
