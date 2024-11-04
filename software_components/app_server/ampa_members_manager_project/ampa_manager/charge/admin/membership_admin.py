import locale
from typing import Optional

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy

from ampa_manager.charge.admin import ERROR_REMITTANCE_NOT_FILLED, ERROR_ONLY_ONE_REMITTANCE
from ampa_manager.charge.admin.filters.receipt_filters import FamilyReceiptFilter
from ampa_manager.charge.models.fee.fee import Fee
from ampa_manager.charge.models.membership_receipt import MembershipReceipt
from ampa_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_manager.charge.remittance import Remittance
from ampa_manager.charge.remittance_utils import RemittanceUtils
from ampa_manager.charge.sepa.sepa_response_creator import SEPAResponseCreator
from ampa_manager.charge.use_cases.membership.create_membership_remittance_for_unique_families.membership_remittance_creator_of_active_course import \
    MembershipRemittanceCreatorOfActiveCourse
from ampa_manager.charge.use_cases.membership.generate_remittance_from_membership_remittance.membership_remittance_generator import \
    MembershipRemittanceGenerator
from ampa_manager.charge.use_cases.remittance_creator_error import RemittanceCreatorError
from ampa_manager.read_only_inline import ReadOnlyTabularInline
from ampa_manager.utils.utils import Utils


class MembershipReceiptInline(ReadOnlyTabularInline):
    model = MembershipReceipt
    extra = 0

    @admin.display(description=gettext_lazy('Course'))
    def remittance_course(self, receipt):
        return receipt.remittance.course


class MembershipRemittanceAdmin(admin.ModelAdmin):
    list_display = ['name', 'sepa_id', 'created_at', 'payment_date', 'receipts_total', 'receipts_count']
    fields = ['name', 'concept', 'sepa_id', 'created_at', 'payment_date', 'receipts_total', 'receipts_link']
    readonly_fields = ['receipts_link', 'created_at', 'receipts_total']
    ordering = ['-created_at']
    list_per_page = 25
    search_fields = ['name', 'concept']

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
        receipts_count = MembershipReceipt.objects.of_remittance(remittance).count()
        if receipts_count == 1:
            link_text = gettext_lazy('%(num_receipts)s receipt') % {'num_receipts': receipts_count}
        else:
            link_text = gettext_lazy('%(num_receipts)s receipts') % {'num_receipts': receipts_count}
        filters = f'remittance={remittance.id}'
        return Utils.get_model_link(model_name=MembershipReceipt.__name__.lower(), link_text=link_text, filters=filters)

    @admin.display(description=gettext_lazy('Total'))
    def receipts_total(self, remittance):
        number_of_receipts = MembershipReceipt.objects.of_remittance(remittance).count()
        fee = Fee.objects.filter(academic_course=remittance.course).first()
        total = 0
        if fee:
            total = number_of_receipts * fee.amount
            locale.setlocale(locale.LC_ALL, 'es_ES')
        return locale.format_string('%.2f €', total, grouping=True)

    @admin.display(description=gettext_lazy('Receipts'))
    def receipts_count(self, remittance):
        return MembershipReceipt.objects.of_remittance(remittance).count()

    @admin.action(description=gettext_lazy("Export Membership remittance to SEPA file"))
    def download_membership_remittance_sepa_file(self, request, queryset: QuerySet[MembershipRemittance]):
        if queryset.count() > 1:
            return self.message_user(request=request, message=gettext_lazy(ERROR_ONLY_ONE_REMITTANCE))
        membership_remittance = queryset.first()
        if not membership_remittance.is_filled():
            return self.message_user(request=request, message=gettext_lazy(ERROR_REMITTANCE_NOT_FILLED))
        remittance: Optional[Remittance]
        remittance_error: Optional[str]
        remittance, remittance_error = MembershipRemittanceGenerator(
            membership_remittance=membership_remittance).generate()
        if remittance is None:
            return self.message_user(request=request, message=remittance_error, level=messages.ERROR)
        return SEPAResponseCreator().create_sepa_response(remittance)

    @admin.action(description=gettext_lazy("Create Membership Remittance with families not included yet"))
    def create_remittance(self, request, _: QuerySet[MembershipRemittance]):
        membership_remittance: Optional[MembershipRemittance]
        remittance_error: Optional[RemittanceCreatorError]
        membership_remittance, remittance_error = MembershipRemittanceCreatorOfActiveCourse.create()
        if not membership_remittance:
            if remittance_error == RemittanceCreatorError.NO_FAMILIES:
                message = gettext_lazy("No families to include in Membership Remittance")
            else:
                if remittance_error == RemittanceCreatorError.BIC_ERROR:
                    message = Utils.create_bic_error_message()
                else:
                    message = gettext_lazy("Membership Remittance error")
            return self.message_user(request=request, message=message, level=messages.ERROR)
        else:
            message = mark_safe(
                gettext_lazy(
                    "Membership remittance created") + " (<a href=\"" + membership_remittance.get_admin_url() + "\">" + gettext_lazy(
                    "View details") + "</a>)")
            return self.message_user(request=request, message=message)

    actions = [download_membership_remittance_sepa_file, create_remittance]


class MembershipReceiptAdmin(admin.ModelAdmin):
    list_display = ['remittance', 'family']
    search_fields = ['family__surnames', 'family__id']
    list_filter = [FamilyReceiptFilter]
    list_per_page = 25
