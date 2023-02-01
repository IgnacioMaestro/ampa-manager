from django.db import models
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.holder.holder import Holder


class CustodyRegistration(models.Model):
    custody_edition = models.ForeignKey(to=CustodyEdition, on_delete=models.CASCADE, verbose_name=_("Custody edition"))
    child = models.ForeignKey(to=Child, on_delete=models.CASCADE, verbose_name=_("Child"))
    holder = models.ForeignKey(to=Holder, on_delete=models.CASCADE, verbose_name=_("Holder"))
    assisted_days = models.PositiveIntegerField()

    class Meta:
        verbose_name = _('Custody registration')
        verbose_name_plural = _('Custody registrations')
        db_table = 'custody_registration'
        constraints = [
            models.UniqueConstraint(fields=['custody_edition', 'child'], name='unique_custody_edition_for_child'),
        ]
