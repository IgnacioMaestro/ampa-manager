from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext as _

from ampa_members_manager.activity.models.activity import Activity
from ampa_members_manager.activity.models.single_activity import SingleActivity


class UniqueActivity(Activity):
    single_activity = models.OneToOneField(verbose_name=_("Single activity"), to=SingleActivity, on_delete=CASCADE)

    class Meta:
        verbose_name = _('Unique activity')
        verbose_name_plural = _('Unique activities')

    def __str__(self) -> str:
        return f'{self.name}'
