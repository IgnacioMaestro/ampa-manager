import codecs
import csv
import locale
from typing import List

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.translation import gettext_lazy

from ampa_manager.read_only_inline import ReadOnlyTabularInline
from . import RECEIPTS_SET_AS_SENT_MESSAGE, RECEIPTS_SET_AS_PAID_MESSAGE, TEXT_CSV
from ..models.after_school_charge.after_school_receipt import AfterSchoolReceipt
from ..models.after_school_charge.after_school_remittance import AfterSchoolRemittance
from ..remittance import Remittance
from ..sepa.response_creator import ResponseCreator
from ..state import State
from ..use_cases.after_school.remittance_generator_from_after_school_remittance import \
    RemittanceGeneratorFromAfterSchoolRemittance


class AfterSchoolReceiptAdmin(admin.ModelAdmin):
    list_display = ['remittance', 'after_school_registration', 'state', 'amount']
    ordering = ['state']
    search_fields = ['after_school_registration__child__family']
    list_filter = ['state']
    list_per_page = 25

    @admin.action(description=gettext_lazy("Set as sent"))
    def set_as_sent(self, request, queryset: QuerySet[AfterSchoolReceipt]):
        queryset.update(state=State.SEND)

        message = gettext_lazy(RECEIPTS_SET_AS_SENT_MESSAGE) % {'num_receipts': queryset.count()}
        self.message_user(request=request, message=message)

    @admin.action(description=gettext_lazy("Set as paid"))
    def set_as_paid(self, request, queryset: QuerySet[AfterSchoolReceipt]):
        queryset.update(state=State.PAID)

        message = gettext_lazy(RECEIPTS_SET_AS_PAID_MESSAGE) % {'num_receipts': queryset.count()}
        self.message_user(request=request, message=message)

    actions = [set_as_sent, set_as_paid]


class AfterSchoolReceiptInline(ReadOnlyTabularInline):
    model = AfterSchoolReceipt
    extra = 0


class AfterSchoolRemittanceAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'receipts_total', 'receipts_count']
    ordering = ['-created_at']
    inlines = [AfterSchoolReceiptInline]
    list_per_page = 25

    @admin.display(description=gettext_lazy('Total'))
    def receipts_total(self, remittance):
        receipts = AfterSchoolReceipt.objects.filter(remittance=remittance)
        total = 0.0
        for receipt in receipts:
            total += receipt.amount
        locale.setlocale(locale.LC_ALL, 'es_ES')
        return locale.format_string('%d €', total, grouping=True)

    @admin.display(description=gettext_lazy('Receipts'))
    def receipts_count(self, remittance):
        return AfterSchoolReceipt.objects.filter(remittance=remittance).count()

    @admin.action(description=gettext_lazy("Export after-school remittance to CSV"))
    def download_membership_remittance_csv(self, request, queryset: QuerySet[AfterSchoolRemittance]):
        if queryset.count() > 1:
            return self.message_user(request=request, message=gettext_lazy("Only can select one membership remittance"))
        remittance: Remittance = RemittanceGeneratorFromAfterSchoolRemittance(
            after_school_remittance=queryset.first()).generate()
        return AfterSchoolRemittanceAdmin.create_csv_response_from_remittance(remittance)

    @admin.action(description=gettext_lazy("Export after-school remittance to SEPA file"))
    def download_membership_remittance_sepa_file(self, request, queryset: QuerySet[AfterSchoolRemittance]):
        if queryset.count() > 1:
            return self.message_user(
                request=request, message=gettext_lazy("Only can select one after-school remittance"))
        after_school_remittance = queryset.first()
        if after_school_remittance.payment_date is None or after_school_remittance.concept is None:
            return self.message_user(
                request=request, message=gettext_lazy(
                    "Concept and payment date must be filled in after-school remittance"))
        remittance: Remittance = RemittanceGeneratorFromAfterSchoolRemittance(
            after_school_remittance=after_school_remittance).generate()
        return ResponseCreator().create(remittance)

    @staticmethod
    def create_csv_response_from_remittance(remittance: Remittance) -> HttpResponse:
        headers = {'Content-Disposition': f'attachment; filename="{remittance.name}.csv"'}
        response = HttpResponse(content_type=TEXT_CSV, headers=headers)
        response.write(codecs.BOM_UTF8)
        rows_to_add: List[List[str]] = [['Titular', 'BIC', 'IBAN', 'Autorizacion', 'Fecha Autorizacion', 'Cantidad']]
        rows_to_add.extend(remittance.obtain_rows())
        csv.writer(response).writerows(rows_to_add)
        return response

    actions = [download_membership_remittance_csv, download_membership_remittance_sepa_file]
