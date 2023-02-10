import codecs
import csv
import locale

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy

from ampa_manager.charge.admin import TEXT_CSV, RECEIPTS_SET_AS_SENT_MESSAGE, RECEIPTS_SET_AS_PAID_MESSAGE
from ampa_manager.charge.models.activity_receipt import ActivityReceipt
from ampa_manager.charge.models.fee.fee import Fee
from ampa_manager.charge.models.membership_receipt import MembershipReceipt
from ampa_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_manager.charge.remittance import Remittance
from ampa_manager.charge.state import State
from ampa_manager.charge.use_cases.membership.create_membership_remittance_for_unique_families.membership_remittance_creator_of_active_course import \
    MembershipRemittanceCreatorOfActiveCourse
from ampa_manager.charge.use_cases.membership.generate_remittance_from_membership_remittance.membership_remittance_generator import \
    MembershipRemittanceGenerator
from ampa_manager.read_only_inline import ReadOnlyTabularInline


class MembershipReceiptInline(ReadOnlyTabularInline):
    model = MembershipReceipt
    extra = 0


class MembershipRemittanceAdmin(admin.ModelAdmin):
    list_display = ['identifier', 'created_at', 'course', 'receipts_total', 'receipts_count']
    ordering = ['-created_at']
    inlines = [MembershipReceiptInline]
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
            return self.message_user(request=request, message=gettext_lazy("Only can select one membership remittance"))
        remittance: Remittance = MembershipRemittanceGenerator(membership_remittance=queryset.first()).generate()
        return MembershipRemittanceAdmin.create_csv_response_from_remittance(remittance)

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
        headers = {'Content-Disposition': f'attachment; filename="{remittance.name}"'}
        response = HttpResponse(content_type=TEXT_CSV, headers=headers)
        response.write(codecs.BOM_UTF8)
        csv.writer(response).writerows(remittance.obtain_rows())
        return response

    actions = [download_membership_remittance_csv, create_remittance]


class MembershipReceiptAdmin(admin.ModelAdmin):
    list_display = ['remittance', 'family', 'state']
    ordering = ['state']
    search_fields = ['family__surnames']
    list_filter = ['state']
    list_per_page = 25

    @admin.action(description=gettext_lazy("Set as sent"))
    def set_as_sent(self, request, queryset: QuerySet[ActivityReceipt]):
        queryset.update(state=State.SEND)

        message = gettext_lazy(RECEIPTS_SET_AS_SENT_MESSAGE) % {'num_receipts': queryset.count()}
        self.message_user(request=request, message=message)

    @admin.action(description=gettext_lazy("Set as paid"))
    def set_as_paid(self, request, queryset: QuerySet[ActivityReceipt]):
        queryset.update(state=State.PAID)

        message = gettext_lazy(RECEIPTS_SET_AS_PAID_MESSAGE) % {'num_receipts': queryset.count()}
        self.message_user(request=request, message=message)

    actions = [set_as_sent, set_as_paid]