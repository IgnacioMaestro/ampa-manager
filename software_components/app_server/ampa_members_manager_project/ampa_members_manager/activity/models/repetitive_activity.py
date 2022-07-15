from django.db import models
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.activity.models.activity import Activity
from ampa_members_manager.activity.models.single_activity import SingleActivity


class RepetitiveActivity(Activity):
    single_activities = models.ManyToManyField(to=SingleActivity, verbose_name=_("Single activities"))

    class Meta:
        verbose_name = _('Repetitive activity')
        verbose_name_plural = _('Repetitive activities')

    def __str__(self) -> str:
        return f'{self.name}'

    @classmethod
    def all_same_repetitive_activity(cls, single_activities: QuerySet[SingleActivity]) -> bool:
        first_single_activity: SingleActivity = single_activities.first()
        repetitive_activity: RepetitiveActivity = first_single_activity.repetitiveactivity_set.first()
        for single_activity in single_activities.all():
            if single_activity.repetitiveactivity_set.first() != repetitive_activity:
                return False
        return True
