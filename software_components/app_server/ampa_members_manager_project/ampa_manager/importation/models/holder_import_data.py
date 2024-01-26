from django.utils.translation import gettext_lazy as _
from localflavor.generic.models import IBANField

from ampa_manager.importation.models.parent_import_data import ParentImportData


class HolderImportData(ParentImportData):
    iban = IBANField(unique=True, verbose_name=_("IBAN"))

    class Meta:
        abstract = True
        verbose_name = _('Holder import data')
        verbose_name_plural = _('Holder import data')
