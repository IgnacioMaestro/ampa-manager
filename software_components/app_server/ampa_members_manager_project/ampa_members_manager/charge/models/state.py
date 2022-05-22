from django.db import models


class State(models.IntegerChoices):
    CREATED = 1
    SEND = 2
    PAID = 3
