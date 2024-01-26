import locale

from django.contrib import admin
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy
from django.utils.translation import gettext_lazy as _

from ampa_manager.read_only_inline import ReadOnlyTabularInline
from . import RECEIPTS_SET_AS_SENT_MESSAGE, RECEIPTS_SET_AS_PAID_MESSAGE, ERROR_REMITTANCE_NOT_FILLED, \
    ERROR_ONLY_ONE_REMITTANCE
from .filters.receipt_filters import CampsReceiptFilter
from ..models.camps.camps_receipt import CampsReceipt
from ..models.camps.camps_remittance import CampsRemittance
from ..remittance import Remittance
from ..sepa.sepa_response_creator import SEPAResponseCreator
from ..state import State
from ..use_cases.camps.remittance_generator_from_camps_remittance import RemittanceGeneratorFromCampsRemittance


class CampsReceiptAdmin(admin.ModelAdmin):
    list_display = ['remittance', 'camps_registration', 'child', 'state', 'amount', 'id']
    ordering = ['state']
    search_fields = ['camps_registration__child__family__surnames',
                     'camps_registration__child__family__id',
                     'camps_registration__child__name',
                     'camps_registration__holder__bank_account__iban',
                     'camps_registration__holder__parent__name_and_surnames']
    list_filter = ['state', CampsReceiptFilter]
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

    @admin.display(description=_('Child'))
    def child(self, camps_receipt):
        return camps_receipt.camps_registration.child.name

    actions = [set_as_sent, set_as_paid]


class CampsReceiptInline(ReadOnlyTabularInline):
    model = CampsReceipt
    extra = 0


class CampsRemittanceAdmin(admin.ModelAdmin):
    list_display = ['name', 'sepa_id', 'created_at', 'payment_date', 'receipts_total', 'receipts_count']
    ordering = ['-created_at']
    list_per_page = 25
    search_fields = ['name', 'concept']

    @admin.display(description=gettext_lazy('Total'))
    def receipts_total(self, remittance):
        total = CampsReceipt.get_total_by_remittance(remittance)
        locale.setlocale(locale.LC_ALL, 'es_ES')
        return locale.format_string('%.2f €', total, grouping=True)

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
