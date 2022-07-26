from django.utils.translation import gettext_lazy as _

from ampa_members_manager.activity.models.activity import Activity


class UniqueActivity(Activity):
    class Meta:
        verbose_name = _('Unique activity')
        verbose_name_plural = _('Unique activities')

    def __str__(self) -> str:
        return f'{self.name}'
