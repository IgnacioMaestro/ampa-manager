from django.db import models
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.camps.camps_edition import CampsEdition
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.holder.holder import Holder


class CampsRegistration(models.Model):
    camps_edition = models.ForeignKey(to=CampsEdition, on_delete=models.CASCADE, verbose_name=_("Camps edition"))
    child = models.ForeignKey(to=Child, on_delete=models.CASCADE, verbose_name=_("Child"))
    holder = models.ForeignKey(to=Holder, on_delete=models.CASCADE, verbose_name=_("Holder"))

    class Meta:
        verbose_name = _('Camps registration')
        verbose_name_plural = _('Camps registrations')
        db_table = 'camps_registration'

        constraints = [
            models.UniqueConstraint(fields=['camps_edition', 'child'], name='unique_camps_edition_for_child'),
        ]
