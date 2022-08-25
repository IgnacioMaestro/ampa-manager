import csv
import codecs

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.charge.state import State
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


class ActivityReceiptAdmin(admin.ModelAdmin):
    list_display = ['remittance', 'amount', 'state']

    @admin.action(description=_("Set as sent"))
    def set_as_sent(self, request, queryset: QuerySet[ActivityReceipt]):
        queryset.update(state=State.SEND)

        message = _("%(num_receipts)s receipts set as sent") % {'num_receipts':  queryset.count()}
        self.message_user(request=request, message=message)
    
    @admin.action(description=_("Set as paid"))
    def set_as_paid(self, request, queryset: QuerySet[ActivityReceipt]):
        queryset.update(state=State.PAID)

        message = _("%(num_receipts)s receipts set as sent") % {'num_receipts':  queryset.count()}
        self.message_user(request=request, message=message)

    list_filter = ['state', 'remittance__name']
    actions = [set_as_sent, set_as_paid]


class ActivityRemittanceAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'receipt_count', 'receipt_created_count', 'receipt_sent_count', 'receipt_paid_count']
    inlines = [ActivityReceiptInline]

    @admin.action(description=_("Export to CSV"))
    def download_csv(self, request, queryset: QuerySet[ActivityRemittance]):
        if queryset.count() > 1:
            return self.message_user(request=request, message=_("Only one activity remittance can be selected at a time"))
        remittance: Remittance = RemittanceGenerator(activity_remittance=queryset.first()).generate()
        return ActivityRemittanceAdmin.create_csv_response_from_remittance(remittance)

    @admin.action(description=_("Set all receipts as sent"))
    def set_all_receipts_as_sent(self, request, queryset: QuerySet[ActivityRemittance]):
        for remittance in queryset:
            remittance.activityreceipt_set.update(state=State.SEND)

            message_vars = {'num_receipts':  remittance.activityreceipt_set.count(), 'remittance': str(remittance)}
            message = _("%(num_receipts)s receipts set as sent for remittance %(remittance)s") % message_vars
            self.message_user(request=request, message=message)
    
    @admin.action(description=_("Set all receipts as paid"))
    def set_all_receipts_as_paid(self, request, queryset: QuerySet[ActivityRemittance]):
        for remittance in queryset:
            remittance.activityreceipt_set.update(state=State.PAID)

            message_vars = {'num_receipts':  remittance.activityreceipt_set.count(), 'remittance': str(remittance)}
            message = _("%(num_receipts)s receipts set as paid for remittance %(remittance)s") % message_vars
            self.message_user(request=request, message=message)

    @staticmethod
    def create_csv_response_from_remittance(remittance: Remittance) -> HttpResponse:
        headers = {'Content-Disposition': f'attachment; filename="{remittance.name}.csv"'}
        response = HttpResponse(content_type='text/csv', headers=headers)
        response.write(codecs.BOM_UTF8)
        csv.writer(response, quoting=csv.QUOTE_ALL).writerows(remittance.obtain_rows())
        return response

    @admin.display(description=_('Total receipts'))
    def receipt_count(self, remittance):
        return remittance.activityreceipt_set.count()
    
    @admin.display(description=_('Created receipts'))
    def receipt_created_count(self, remittance):
        return remittance.activityreceipt_set.filter(state=State.CREATED).count()
    
    @admin.display(description=_('Sent receipts'))
    def receipt_sent_count(self, remittance):
        return remittance.activityreceipt_set.filter(state=State.SEND).count()

    @admin.display(description=_('Paid receipts'))
    def receipt_paid_count(self, remittance):
        return remittance.activityreceipt_set.filter(state=State.PAID).count()

    actions = [download_csv, set_all_receipts_as_sent, set_all_receipts_as_paid]


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
        response.write(codecs.BOM_UTF8)
        csv.writer(response).writerows(remittance.obtain_rows())
        return response

    actions = [download_membership_remittance_csv]
