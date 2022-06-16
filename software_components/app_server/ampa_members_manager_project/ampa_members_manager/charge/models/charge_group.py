import csv

from __future__ import annotations
from django.db import models, transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse

from ampa_members_manager.activity.models.single_activity import SingleActivity


class NoSingleActivityError(Exception):
    def __init__(self):
        super().__init__("NoSingleActivityError")


class ChargeGroup(models.Model):
    single_activities = models.ManyToManyField(to=SingleActivity, verbose_name=_("Single activities"))

    class Meta:
        verbose_name = _('Charge group')
        verbose_name_plural = _('Charge groups')

    #@admin.action(description='Export selected charge groups to a CSV file')
    @staticmethod
    def download_csv(modeladmin, request, queryset):
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="charge_groups.csv"'},
        )

        writer = csv.writer(response)
        for charge_group in queryset:
            for charge in charge_group.charge_set.all():
                receipt = charge.generate_receipt()
                writer.writerow(receipt.export_csv())

        return response

    @classmethod
    def create_filled_charge_group(cls, single_activities: QuerySet[SingleActivity]) -> ChargeGroup:
        if not single_activities.exists():
            raise NoSingleActivityError

        with transaction.atomic():
            charge_group: ChargeGroup = ChargeGroup.objects.create()
            charge_group.single_activities.set(single_activities)
            return charge_group
