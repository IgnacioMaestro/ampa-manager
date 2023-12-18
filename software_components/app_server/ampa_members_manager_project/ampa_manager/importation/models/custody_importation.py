from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.importation.models.importation import Importation


class CustodyImportation(Importation):
    custody_edition = models.ForeignKey(to=CustodyEdition, on_delete=CASCADE, verbose_name=_("Custody Edition"))

    class Meta:
        verbose_name = _('Custody importation')
        verbose_name_plural = _('Custody importations')
        db_table = 'custody_importation'
