from django.db import models
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.funding import Funding
from ampa_manager.management.commands.results.processing_state import ProcessingState


class AfterSchool(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("AfterSchool activity name"), unique=True)
    funding = models.IntegerField(choices=Funding.choices, verbose_name=_("Funding"))

    class Meta:
        verbose_name = _('After-school')
        verbose_name_plural = _('After-schools')
        db_table = 'after_school'

    def __str__(self) -> str:
        return f'{self.name}'

    @staticmethod
    def find(name):
        try:
            return AfterSchool.objects.get(name=name)
        except AfterSchool.DoesNotExist:
            return None

    @staticmethod
    def import_after_school(name):
        after_school = AfterSchool.find(name)
        if after_school:
            return after_school, ProcessingState.NOT_MODIFIED, None
        else:
            return None, ProcessingState.ERROR, f'Not found: "{name}"'
