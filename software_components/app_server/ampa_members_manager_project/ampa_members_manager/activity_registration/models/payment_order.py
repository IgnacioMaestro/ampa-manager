from django.db import models


class PaymentOrder(models.Model):
    amount = models.FloatField()
