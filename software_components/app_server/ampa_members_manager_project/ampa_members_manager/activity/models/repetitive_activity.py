from django.utils.translation import gettext_lazy as _

from ampa_members_manager.activity.models.activity import Activity


class RepetitiveActivity(Activity):
    class Meta:
        verbose_name = _('Repetitive activity')
        verbose_name_plural = _('Repetitive activities')

    def __str__(self) -> str:
        return f'{self.name}'
