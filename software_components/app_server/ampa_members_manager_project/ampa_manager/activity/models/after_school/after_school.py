from django.db import models
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.funding import Funding


class AfterSchool(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("AfterSchool activity name"), unique=True)
    funding = models.IntegerField(choices=Funding.choices, verbose_name=_("Funding"))

    class Meta:
        verbose_name = _('Activity')
        verbose_name_plural = _('Activities')
        db_table = 'after_school'

    def __str__(self) -> str:
        return f'{self.name}'
