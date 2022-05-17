from django.db import models
from django.utils.translation import gettext as _

from ampa_members_manager.activity.models.activity import Activity
from ampa_members_manager.activity.models.single_activity import SingleActivity


class RepetitiveActivity(Activity):
    single_activities = models.ManyToManyField(verbose_name=_("Single activities"), to=SingleActivity)

    def __str__(self) -> str:
        return f'{self.name}'
