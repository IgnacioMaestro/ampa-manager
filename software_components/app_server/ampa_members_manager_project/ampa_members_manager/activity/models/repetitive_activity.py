from django.db import models
from django.utils.translation import gettext as _

from ampa_members_manager.activity.models.activity import Activity
from ampa_members_manager.activity.models.single_activity import SingleActivity


class RepetitiveActivity(Activity):
    single_activities = models.ManyToManyField(verbose_name=_("Single activities"), to=SingleActivity)

    class Meta:
        verbose_name = _('Repetitive activity')
        verbose_name_plural = _('Repetitive activities')

    def __str__(self) -> str:
        return f'{self.name}'
