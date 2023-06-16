import locale

from django.contrib import admin
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy

from ampa_manager.read_only_inline import ReadOnlyTabularInline
from . import RECEIPTS_SET_AS_SENT_MESSAGE, RECEIPTS_SET_AS_PAID_MESSAGE, ERROR_REMITTANCE_NOT_FILLED, \
    ERROR_ONLY_ONE_REMITTANCE
from ..models.camps.camps_receipt import CampsReceipt
from ..models.camps.camps_remittance import CampsRemittance
from ..remittance import Remittance
from ..sepa.sepa_response_creator import SEPAResponseCreator
from ..state import State
from ..use_cases.camps.remittance_generator_from_camps_remittance import RemittanceGeneratorFromCampsRemittance


class CampsReceiptAdmin(admin.ModelAdmin):
    list_display = ['remittance', 'camps_registration', 'state', 'amount']
    ordering = ['state']
    search_fields = ['camps_registration__child__family']
    list_filter = ['state']
    list_per_page = 25

    @admin.action(description=gettext_lazy("Set as sent"))
    def set_as_sent(self, request, queryset: QuerySet[CampsReceipt]):
        queryset.update(state=State.SEND)

        message = gettext_lazy(RECEIPTS_SET_AS_SENT_MESSAGE) % {'num_receipts': queryset.count()}
        self.message_user(request=request, message=message)

    @admin.action(description=gettext_lazy("Set as paid"))
    def set_as_paid(self, request, queryset: QuerySet[CampsReceipt]):
        queryset.update(state=State.PAID)

        message = gettext_lazy(RECEIPTS_SET_AS_PAID_MESSAGE) % {'num_receipts': queryset.count()}
        self.message_user(request=request, message=message)

    actions = [set_as_sent, set_as_paid]


class CampsReceiptInline(ReadOnlyTabularInline):
    model = CampsReceipt
    extra = 0


class CampsRemittanceAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'receipts_total', 'receipts_count', 'sepa_id']
    ordering = ['-created_at']
    inlines = [CampsReceiptInline]
    list_per_page = 25

    @admin.display(description=gettext_lazy('Total'))
    def receipts_total(self, remittance):
        receipts = CampsReceipt.objects.filter(remittance=remittance)
        total = 0.0
        for receipt in receipts:
            total += receipt.amount
        locale.setlocale(locale.LC_ALL, 'es_ES')
        return locale.format_string('%d €', total, grouping=True)

    @admin.display(description=gettext_lazy('Receipts'))
    def receipts_count(self, remittance):
        return CampsReceipt.objects.filter(remittance=remittance).count()

    @admin.action(description=gettext_lazy("Export camps remittance to SEPA file"))
    def download_membership_remittance_sepa_file(self, request, queryset: QuerySet[CampsRemittance]):
        if queryset.count() > 1:
            return self.message_user(request=request, message=gettext_lazy(ERROR_ONLY_ONE_REMITTANCE))
        camps_remittance = queryset.first()
        if not camps_remittance.is_filled():
            return self.message_user(request=request, message=gettext_lazy(ERROR_REMITTANCE_NOT_FILLED))
        remittance: Remittance = RemittanceGeneratorFromCampsRemittance(
            camps_remittance=camps_remittance).generate()
        return SEPAResponseCreator().create_sepa_response(remittance)

    actions = [download_membership_remittance_sepa_file]
