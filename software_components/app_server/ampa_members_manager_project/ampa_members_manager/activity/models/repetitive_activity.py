from django.db import models

from ampa_members_manager.activity.models.activity import Activity
from ampa_members_manager.activity.models.single_activity import SingleActivity


class RepetitiveActivity(Activity):
    single_activities = models.ManyToManyField(to=SingleActivity)

    def __str__(self) -> str:
        return f'{self.name}'
