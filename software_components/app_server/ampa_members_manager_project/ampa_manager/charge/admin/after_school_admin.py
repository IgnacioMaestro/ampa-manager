import locale
from typing import Optional

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy
from django.utils.translation import gettext_lazy as _

from ampa_manager.read_only_inline import ReadOnlyTabularInline
from . import RECEIPTS_SET_AS_SENT_MESSAGE, RECEIPTS_SET_AS_PAID_MESSAGE, ERROR_REMITTANCE_NOT_FILLED, \
    ERROR_ONLY_ONE_REMITTANCE
from .filters.receipt_filters import FamilyReceiptFilter
from ..models.after_school_charge.after_school_receipt import AfterSchoolReceipt
from ..models.after_school_charge.after_school_remittance import AfterSchoolRemittance
from ..remittance import Remittance
from ..remittance_utils import RemittanceUtils
from ..sepa.sepa_response_creator import SEPAResponseCreator
from ..state import State
from ..use_cases.after_school.remittance_generator_from_after_school_remittance import \
    RemittanceGeneratorFromAfterSchoolRemittance
from ..use_cases.remittance_creator_error import RemittanceCreatorError
from ...utils.utils import Utils


class AfterSchoolReceiptAdmin(admin.ModelAdmin):
    list_display = ['remittance', 'holder', 'child', 'rounded_amount', 'id']
    ordering = ['state']
    search_fields = ['after_school_registration__child__family__surnames',
                     'after_school_registration__child__family__id',
                     'after_school_registration__child__name',
                     'after_school_registration__holder__bank_account__iban',
                     'after_school_registration__parent__name_and_surnames']
    list_filter = ['state', FamilyReceiptFilter]
    list_per_page = 25

    @admin.display(description=_('Child'))
    def child(self, camps_receipt):
        return camps_receipt.after_school_registration.child.name

    @admin.display(description=gettext_lazy('Holder'))
    def holder(self, receipt):
        return receipt.after_school_registration.holder

    @admin.display(description=gettext_lazy('Total'))
    def rounded_amount(self, receipt):
        if receipt.amount:
            return round(receipt.amount, 2)
        return None

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
    list_display = ['name', 'sepa_id', 'created_at', 'payment_date', 'receipts_total', 'receipts_count']
    fields = ['name', 'concept', 'sepa_id', 'created_at', 'payment_date', 'receipts_total', 'receipts_link']
    readonly_fields = ['receipts_link', 'created_at', 'receipts_total']
    ordering = ['-created_at']
    list_per_page = 25

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['sepa_id'].initial = RemittanceUtils.get_next_sepa_id()
        return form

    def save_model(self, request, obj, form, change):
        if not obj.sepa_id:
            obj.sepa_id = RemittanceUtils.get_next_sepa_id()
        super().save_model(request, obj, form, change)

    @admin.display(description=gettext_lazy('Receipts'))
    def receipts_link(self, remittance):
        receipts_count = AfterSchoolReceipt.objects.of_remittance(remittance).count()
        if receipts_count == 1:
            link_text = gettext_lazy('%(num_receipts)s receipt') % {'num_receipts': receipts_count}
        else:
            link_text = gettext_lazy('%(num_receipts)s receipts') % {'num_receipts': receipts_count}
        filters = f'remittance={remittance.id}'
        return Utils.get_model_link(
            model_name=AfterSchoolReceipt.__name__.lower(), link_text=link_text, filters=filters)

    @admin.display(description=gettext_lazy('Total'))
    def receipts_total(self, remittance):
        total = AfterSchoolReceipt.get_total_by_remittance(remittance)
        locale.setlocale(locale.LC_ALL, 'es_ES')
        return locale.format_string('%.2f €', total, grouping=True)

    @admin.display(description=gettext_lazy('Receipts'))
    def receipts_count(self, remittance):
        return AfterSchoolReceipt.objects.filter(remittance=remittance).count()

    @admin.action(description=gettext_lazy("Export after-school remittance to SEPA file"))
    def download_membership_remittance_sepa_file(self, request, queryset: QuerySet[AfterSchoolRemittance]):
        if queryset.count() > 1:
            return self.message_user(request=request, message=gettext_lazy(ERROR_ONLY_ONE_REMITTANCE))
        after_school_remittance = queryset.first()
        if not after_school_remittance.is_filled():
            return self.message_user(request=request, message=gettext_lazy(ERROR_REMITTANCE_NOT_FILLED))
        remittance: Optional[Remittance]
        remittance_error: Optional[RemittanceCreatorError]
        remittance, remittance_error = RemittanceGeneratorFromAfterSchoolRemittance(
            after_school_remittance=after_school_remittance).generate()
        if remittance_error == RemittanceCreatorError.BIC_ERROR:
            message = Utils.create_bic_error_message()
            return self.message_user(request=request, message=message, level=messages.ERROR)
        return SEPAResponseCreator().create_sepa_response(remittance)

    actions = [download_membership_remittance_sepa_file]
