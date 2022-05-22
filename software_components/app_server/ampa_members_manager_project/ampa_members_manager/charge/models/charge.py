from django.db import models
from django.db.models import CASCADE

from ampa_members_manager.activity_registration.models.activity_registration import ActivityRegistration
from ampa_members_manager.charge.models.charge_group import ChargeGroup
from ampa_members_manager.charge.models.state import State


class Charge(models.Model):
    amount = models.FloatField(null=True, blank=True)
    state = models.IntegerField(choices=State.choices, default=State.CREATED)
    activity_registrations = models.ManyToManyField(to=ActivityRegistration)
    group = models.ForeignKey(to=ChargeGroup, on_delete=CASCADE)
