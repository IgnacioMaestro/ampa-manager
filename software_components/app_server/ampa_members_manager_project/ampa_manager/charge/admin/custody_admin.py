import locale
from typing import Optional

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy
from django.utils.translation import gettext_lazy as _

from ampa_manager.read_only_inline import ReadOnlyTabularInline
from . import ERROR_REMITTANCE_NOT_FILLED, ERROR_ONLY_ONE_REMITTANCE
from .filters.receipt_filters import FamilyReceiptFilter, ParentReceiptFilter
from ..models.custody.custody_receipt import CustodyReceipt
from ..models.custody.custody_remittance import CustodyRemittance
from ..remittance import Remittance
from ..remittance_utils import RemittanceUtils
from ..sepa.sepa_response_creator import SEPAResponseCreator
from ..use_cases.custody.remittance_generator_from_custody_remittance import RemittanceGeneratorFromCustodyRemittance
from ..use_cases.remittance_creator_error import RemittanceCreatorError
from ...family.use_cases.family_emails_exporter import FamilyEmailExporter
from ...utils.csv_http_response import CsvHttpResponse
from ...utils.currency_utils import CurrencyUtils
from ...utils.utils import Utils


class CustodyReceiptAdmin(admin.ModelAdmin):
    list_display = ['remittance', 'holder', 'child', 'rounded_amount', 'id']
    fields = ['remittance', 'custody_registration', 'amount', 'id']
    readonly_fields = ['id']
    search_fields = ['custody_registration__child__family__surnames',
                     'custody_registration__child__family__id',
                     'custody_registration__child__name',
                     'custody_registration__holder__bank_account__iban',
                     'custody_registration__holder__parent__name_and_surnames']
    list_filter = ['amount', FamilyReceiptFilter, ParentReceiptFilter]
    list_per_page = 25

    @admin.display(description=_('Child'))
    def child(self, camps_receipt):
        return camps_receipt.custody_registration.child.name

    @admin.display(description=gettext_lazy('Holder'))
    def holder(self, receipt):
        return receipt.custody_registration.holder

    @admin.display(description=gettext_lazy('Total'))
    def rounded_amount(self, receipt):
        return CurrencyUtils.get_rounded_amount(receipt.amount)


class CustodyReceiptInline(ReadOnlyTabularInline):
    model = CustodyReceipt
    extra = 0


class CustodyRemittanceAdmin(admin.ModelAdmin):
    list_display = ['name', 'sepa_id', 'created_at', 'payment_date', 'receipts_total', 'receipts_count']
    fields = ['name', 'concept', 'sepa_id', 'created_at', 'payment_date', 'receipts_total', 'receipts_link']
    readonly_fields = ['receipts_link', 'created_at', 'receipts_total', 'sepa_id']
    ordering = ['-created_at']
    list_per_page = 25
    search_fields = ['name', 'concept', 'sepa_id']

    def save_model(self, request, obj, form, change):
        if not obj.sepa_id:
            obj.sepa_id = RemittanceUtils.get_next_sepa_id()
        super().save_model(request, obj, form, change)

    @admin.display(description=gettext_lazy('Receipts'))
    def receipts_link(self, remittance):
        receipts_count = CustodyReceipt.objects.of_remittance(remittance).count()
        if receipts_count == 1:
            link_text = gettext_lazy('%(num_receipts)s receipt') % {'num_receipts': receipts_count}
        else:
            link_text = gettext_lazy('%(num_receipts)s receipts') % {'num_receipts': receipts_count}
        filters = f'remittance={remittance.id}'
        return Utils.get_model_link(model_name=CustodyReceipt.__name__.lower(), link_text=link_text, filters=filters)

    @admin.display(description=gettext_lazy('Total'))
    def receipts_total(self, remittance):
        total = CustodyReceipt.get_total_by_remittance(remittance)
        locale.setlocale(locale.LC_ALL, 'es_ES')
        return locale.format_string('%.2f €', total, grouping=True)

    @admin.display(description=gettext_lazy('Receipts'))
    def receipts_count(self, remittance):
        return CustodyReceipt.objects.filter(remittance=remittance).count()

    @admin.action(description=gettext_lazy("Export custody remittance to SEPA file"))
    def download_membership_remittance_sepa_file(self, request, queryset: QuerySet[CustodyRemittance]):
        if queryset.count() > 1:
            return self.message_user(request=request, message=gettext_lazy(ERROR_ONLY_ONE_REMITTANCE))
        custody_remittance = queryset.first()
        if not custody_remittance.is_filled():
            return self.message_user(request=request, message=gettext_lazy(ERROR_REMITTANCE_NOT_FILLED))
        remittance: Optional[Remittance]
        error: Optional[RemittanceCreatorError]
        remittance, error = RemittanceGeneratorFromCustodyRemittance(custody_remittance=custody_remittance).generate()
        if error == RemittanceCreatorError.BIC_ERROR:
            message = Utils.create_bic_error_message()
            return self.message_user(request=request, message=message, level=messages.ERROR)
        return SEPAResponseCreator().create_sepa_response(remittance)

    @admin.action(description=gettext_lazy("Export family emails to CSV"))
    def download_families_emails(self, request, remittances: QuerySet[CustodyRemittance]):
        families = []
        for remittance in remittances.all():
            receipt: CustodyReceipt
            for receipt in remittance.receipts.all():
                families.append(receipt.custody_registration.child.family)
        emails_csv = FamilyEmailExporter(families).export_to_csv()
        return CsvHttpResponse('correos.csv', emails_csv)

    actions = [download_membership_remittance_sepa_file, download_families_emails]
