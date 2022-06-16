import csv
from datetime import datetime

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

    @staticmethod
    def download_csv(modeladmin, request, queryset):
        filename = 'charge_groups_' + datetime.now().strftime("%m%d%Y_%H%M%S") + '.csv'
        response = HttpResponse(
            content_type='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            },
        )

        writer = csv.writer(response)
        for charge_group in queryset.all():
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
