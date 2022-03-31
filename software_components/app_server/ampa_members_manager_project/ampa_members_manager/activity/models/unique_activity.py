from django.db import models
from django.db.models import CASCADE

from ampa_members_manager.activity.models.activity import Activity
from ampa_members_manager.activity.models.single_activity import SingleActivity


class UniqueActivity(Activity):
    single_activity = models.OneToOneField(to=SingleActivity, on_delete=CASCADE)

    def __str__(self) -> str:
        return f'{self.name}'
