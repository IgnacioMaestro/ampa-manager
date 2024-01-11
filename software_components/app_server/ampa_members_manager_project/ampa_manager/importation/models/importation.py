from django.db import models
from django.utils.translation import gettext_lazy as _


class Importation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    filename = models.CharField(max_length=255, verbose_name=_("Filename"))

    class Meta:
        abstract = True
        verbose_name = _("Importation")
        verbose_name_plural = _("Importations")
