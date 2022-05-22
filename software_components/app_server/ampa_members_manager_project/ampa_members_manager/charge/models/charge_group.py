from django.db import models

from ampa_members_manager.activity.models.single_activity import SingleActivity


class ChargeGroup(models.Model):
    single_activities = models.ManyToManyField(to=SingleActivity)

