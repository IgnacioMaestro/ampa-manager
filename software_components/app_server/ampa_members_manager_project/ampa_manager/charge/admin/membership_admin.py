import locale

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy

from ampa_manager.charge.admin import RECEIPTS_SET_AS_SENT_MESSAGE, RECEIPTS_SET_AS_PAID_MESSAGE, \
    ERROR_REMITTANCE_NOT_FILLED, ERROR_ONLY_ONE_REMITTANCE
from ampa_manager.charge.admin.csv_response_creator import CSVResponseCreator
from ampa_manager.charge.models.fee.fee import Fee
from ampa_manager.charge.models.membership_receipt import MembershipReceipt
from ampa_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_manager.charge.remittance import Remittance
from ampa_manager.charge.sepa.sepa_response_creator import SEPAResponseCreator
from ampa_manager.charge.state import State
from ampa_manager.charge.use_cases.membership.create_membership_remittance_for_unique_families.membership_remittance_creator_of_active_course import \
    MembershipRemittanceCreatorOfActiveCourse
from ampa_manager.charge.use_cases.membership.generate_remittance_from_membership_remittance.membership_remittance_generator import \
    MembershipRemittanceGenerator
from ampa_manager.read_only_inline import ReadOnlyTabularInline


class MembershipReceiptInline(ReadOnlyTabularInline):
    model = MembershipReceipt
    extra = 0

    @admin.display(description=gettext_lazy('Course'))
    def remittance_course(self, receipt):
        return receipt.remittance.course


class MembershipRemittanceAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'course', 'receipts_total', 'receipts_count', 'sepa_id', 'payment_date']
    fields = ['name', 'course', 'sepa_id', 'payment_date', 'concept', 'receipts_count', 'receipts_total', 'created_at']
    readonly_fields = ['created_at', 'receipts_total', 'receipts_count']
    ordering = ['-created_at']
    # inlines = [MembershipReceiptInline]
    list_per_page = 25

    @admin.display(description=gettext_lazy('Total'))
    def receipts_total(self, remittance):
        number_of_receipts = MembershipReceipt.objects.of_remittance(remittance).count()
        fee = Fee.objects.filter(academic_course=remittance.course).first()
        if fee:
            total = number_of_receipts * fee.amount
            locale.setlocale(locale.LC_ALL, 'es_ES')
            return locale.format_string('%d €', total, grouping=True)
        return '0 €'

    @admin.display(description=gettext_lazy('Receipts'))
    def receipts_count(self, remittance):
        return MembershipReceipt.objects.of_remittance(remittance).count()

    @admin.action(description=gettext_lazy("Export Membership Remittance to CSV"))
    def download_membership_remittance_csv(self, request, queryset: QuerySet[MembershipRemittance]):
        if queryset.count() > 1:
            return self.message_user(request=request, message=gettext_lazy(ERROR_ONLY_ONE_REMITTANCE))
        remittance: Remittance = MembershipRemittanceGenerator(membership_remittance=queryset.first()).generate()
        return MembershipRemittanceAdmin.create_csv_response_from_remittance(remittance)

    @admin.action(description=gettext_lazy("Export Membership remittance to SEPA file"))
    def download_membership_remittance_sepa_file(self, request, queryset: QuerySet[MembershipRemittance]):
        if queryset.count() > 1:
            return self.message_user(request=request, message=gettext_lazy(ERROR_ONLY_ONE_REMITTANCE))
        membership_remittance = queryset.first()
        if not membership_remittance.is_filled():
            return self.message_user(request=request, message=gettext_lazy(ERROR_REMITTANCE_NOT_FILLED))
        remittance: Remittance = MembershipRemittanceGenerator(membership_remittance=membership_remittance).generate()
        return SEPAResponseCreator().create_sepa_response(remittance)

    @admin.action(description=gettext_lazy("Create Membership Remittance with families not included yet"))
    def create_remittance(self, request, _: QuerySet[MembershipRemittance]):
        membership_remittance: MembershipRemittance = MembershipRemittanceCreatorOfActiveCourse.create()
        if membership_remittance:
            message = mark_safe(
                gettext_lazy(
                    "Membership remittance created") + " (<a href=\"" + membership_remittance.get_admin_url() + "\">" + gettext_lazy(
                    "View details") + "</a>)")
            return self.message_user(request=request, message=message)
        else:
            message = gettext_lazy("No families to include in Membership Remittance")
            return self.message_user(request=request, message=message)

    @staticmethod
    def create_csv_response_from_remittance(remittance: Remittance) -> HttpResponse:
        return CSVResponseCreator(remittance=remittance).create()

    actions = [download_membership_remittance_csv, download_membership_remittance_sepa_file, create_remittance]


class MembershipReceiptAdmin(admin.ModelAdmin):
    list_display = ['remittance', 'family', 'state']
    ordering = ['state']
    search_fields = ['family__surnames']
    list_filter = ['state']
    list_per_page = 25

    @admin.action(description=gettext_lazy("Set as sent"))
    def set_as_sent(self, request, queryset: QuerySet[MembershipReceipt]):
        queryset.update(state=State.SEND)

        message = gettext_lazy(RECEIPTS_SET_AS_SENT_MESSAGE) % {'num_receipts': queryset.count()}
        self.message_user(request=request, message=message)

    @admin.action(description=gettext_lazy("Set as paid"))
    def set_as_paid(self, request, queryset: QuerySet[MembershipReceipt]):
        queryset.update(state=State.PAID)

        message = gettext_lazy(RECEIPTS_SET_AS_PAID_MESSAGE) % {'num_receipts': queryset.count()}
        self.message_user(request=request, message=message)

    actions = [set_as_sent, set_as_paid]
