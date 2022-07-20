import csv
import codecs

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.charge.models.charge import Charge
from ampa_members_manager.charge.models.charge_group import ChargeGroup
from ampa_members_manager.charge.remittance import Remittance
from ampa_members_manager.charge.use_cases.generate_remittance_from_charge_group.remittance_generator import \
    RemittanceGenerator


class ChargeInline(admin.TabularInline):
    model = Charge
    extra = 0


class ChargeGroupAdmin(admin.ModelAdmin):
    inlines = [ChargeInline]

    @admin.action(description=_("Export to CSV"))
    def download_csv(self, request, queryset: QuerySet[ChargeGroup]):
        if queryset.count() > 1:
            return self.message_user(request=request, message=_("Only one charge group can be selected at a time"))
        remittance: Remittance = RemittanceGenerator(charge_group=queryset.first()).generate()
        return ChargeGroupAdmin.create_csv_response_from_remittance(remittance)

    @staticmethod
    def create_csv_response_from_remittance(remittance: Remittance) -> HttpResponse:
        headers = {'Content-Disposition': f'attachment; filename="{remittance.name}.csv"'}
        response = HttpResponse(content_type='text/csv', headers=headers)
        response.write(codecs.BOM_UTF8)
        csv.writer(response).writerows(remittance.obtain_rows())
        return response

    actions = [download_csv]
