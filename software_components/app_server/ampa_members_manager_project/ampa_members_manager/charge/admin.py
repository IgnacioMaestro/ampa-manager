import csv
import codecs

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.charge.models.activity_receipt import ActivityReceipt
from ampa_members_manager.charge.models.activity_remittance import ActivityRemittance
from ampa_members_manager.charge.models.membership_receipt import MembershipReceipt
from ampa_members_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_members_manager.charge.remittance import Remittance
from ampa_members_manager.charge.use_cases.generate_remittance_from_activity_remittance.remittance_generator import \
    RemittanceGenerator
from ampa_members_manager.charge.use_cases.generate_remittance_from_membership_remittance.membership_remittance_generator import \
    MembershipRemittanceGenerator


class ActivityReceiptInline(admin.TabularInline):
    model = ActivityReceipt
    extra = 0


class ActivityRemittanceAdmin(admin.ModelAdmin):
    inlines = [ActivityReceiptInline]

    @admin.action(description=_("Export to CSV"))
    def download_csv(self, request, queryset: QuerySet[ActivityRemittance]):
        if queryset.count() > 1:
            return self.message_user(request=request, message=_("Only one activity remittance can be selected at a time"))
        remittance: Remittance = RemittanceGenerator(activity_remittance=queryset.first()).generate()
        return ActivityRemittanceAdmin.create_csv_response_from_remittance(remittance)

    @staticmethod
    def create_csv_response_from_remittance(remittance: Remittance) -> HttpResponse:
        headers = {'Content-Disposition': f'attachment; filename="{remittance.name}.csv"'}
        response = HttpResponse(content_type='text/csv', headers=headers)
        response.write(codecs.BOM_UTF8)
        csv.writer(response).writerows(remittance.obtain_rows())
        return response

    actions = [download_csv]


class MembershipReceiptInline(admin.TabularInline):
    model = MembershipReceipt
    extra = 0


class MembershipRemittanceAdmin(admin.ModelAdmin):
    inlines = [MembershipReceiptInline]

    @admin.action(description=_("Export Membership Remittance to CSV"))
    def download_membership_remittance_csv(self, request, queryset: QuerySet[MembershipRemittance]):
        if queryset.count() > 1:
            return self.message_user(request=request, message=_("Only can select one membership remittance"))
        remittance: Remittance = MembershipRemittanceGenerator(membership_remittance=queryset.first()).generate()
        return MembershipRemittanceAdmin.create_csv_response_from_remittance(remittance)

    @staticmethod
    def create_csv_response_from_remittance(remittance: Remittance) -> HttpResponse:
        headers = {'Content-Disposition': f'attachment; filename="{remittance.name}"'}
        response = HttpResponse(content_type='text/csv', headers=headers)
        csv.writer(response).writerows(remittance.obtain_rows())
        return response

    actions = [download_membership_remittance_csv]
