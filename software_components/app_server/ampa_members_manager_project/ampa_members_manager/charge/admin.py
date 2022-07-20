import csv

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.charge.models.activity_receipt import ActivityReceipt
from ampa_members_manager.charge.models.activity_remittance import ActivityRemittance
from ampa_members_manager.charge.remittance import Remittance
from ampa_members_manager.charge.use_cases.generate_remittance_from_charge_group.remittance_generator import \
    RemittanceGenerator


class ActivityReceiptInline(admin.TabularInline):
    model = ActivityReceipt
    extra = 0


class ChargeGroupAdmin(admin.ModelAdmin):
    inlines = [ActivityReceiptInline]

    @admin.action(description=_("Export to CSV"))
    def download_csv(self, request, queryset: QuerySet[ActivityRemittance]):
        if queryset.count() > 1:
            return self.message_user(request=request, message=_("Only can select one charge group"))
        remittance: Remittance = RemittanceGenerator(charge_group=queryset.first()).generate()
        return ChargeGroupAdmin.create_csv_response_from_remittance(remittance)

    @staticmethod
    def create_csv_response_from_remittance(remittance: Remittance) -> HttpResponse:
        headers = {'Content-Disposition': f'attachment; filename="{remittance.name}"'}
        response = HttpResponse(content_type='text/csv', headers=headers)
        csv.writer(response).writerows(remittance.obtain_rows())
        return response

    actions = [download_csv]
