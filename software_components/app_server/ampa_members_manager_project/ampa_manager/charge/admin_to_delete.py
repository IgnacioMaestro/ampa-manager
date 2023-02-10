import codecs
import csv

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.translation import gettext_lazy

from ampa_manager.read_only_inline import ReadOnlyTabularInline
from .models.activity_receipt import ActivityReceipt
from .models.activity_remittance import ActivityRemittance
from .remittance import Remittance
from .state import State
from .use_cases.activity.generate_remittance_from_activity_remittance.remittance_generator import RemittanceGenerator


class ActivityReceiptInline(ReadOnlyTabularInline):
    model = ActivityReceipt
    extra = 0


class ActivityReceiptAdmin(admin.ModelAdmin):
    list_display = ['remittance', 'amount', 'state', 'activity_registrations_count', 'family', 'children', 'activities']
    ordering = ['remittance', 'state']
    list_per_page = 25

    @admin.action(description=gettext_lazy("Set as sent"))
    def set_as_sent(self, request, queryset: QuerySet[ActivityReceipt]):
        queryset.update(state=State.SEND)

        message = gettext_lazy("%(num_receipts)s receipts set as sent") % {'num_receipts': queryset.count()}
        self.message_user(request=request, message=message)

    @admin.action(description=gettext_lazy("Set as paid"))
    def set_as_paid(self, request, queryset: QuerySet[ActivityReceipt]):
        queryset.update(state=State.PAID)

        message = gettext_lazy("%(num_receipts)s receipts set as paid") % {'num_receipts': queryset.count()}
        self.message_user(request=request, message=message)

    @admin.display(description=gettext_lazy('Family'))
    def family(self, activity_receipt):
        families = []
        for activity_registration in activity_receipt.activity_registrations.all():
            if activity_registration.child.family.surnames not in families:
                families.append(activity_registration.child.family.surnames)
        return ', '.join(families)

    @admin.display(description=gettext_lazy('Children'))
    def children(self, activity_receipt):
        children_list = []
        for activity_registration in activity_receipt.activity_registrations.all():
            if activity_registration.child.name not in children_list:
                children_list.append(activity_registration.child.name)
        return ', '.join(children_list)

    @admin.display(description=gettext_lazy('Activities'))
    def activities(self, activity_receipt):
        activities_list = []
        for activity_registration in activity_receipt.activity_registrations.all():
            if str(activity_registration.activity_period) not in activities_list:
                activities_list.append(str(activity_registration.activity_period))
        return ', '.join(activities_list)

    @admin.display(description=gettext_lazy('Activities'))
    def activity_registrations_count(self, activity_receipt):
        return activity_receipt.activity_registrations.count()

    list_filter = ['state', 'remittance__name']
    actions = [set_as_sent, set_as_paid]


class ActivityRemittanceAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'name', 'receipt_count', 'receipt_created_count', 'receipt_sent_count',
                    'receipt_paid_count']
    ordering = ['-created_at']
    list_filter = ['created_at']
    inlines = [ActivityReceiptInline]
    list_per_page = 25

    @admin.action(description=gettext_lazy("Export to CSV"))
    def download_csv(self, request, queryset: QuerySet[ActivityRemittance]):
        if queryset.count() > 1:
            return self.message_user(
                request=request,
                message=gettext_lazy("Only one activity remittance can be selected at a time"))
        remittance: Remittance = RemittanceGenerator(activity_remittance=queryset.first()).generate()
        return ActivityRemittanceAdmin.create_csv_response_from_remittance(remittance)

    @admin.action(description=gettext_lazy("Set all receipts as sent"))
    def set_all_receipts_as_sent(self, request, queryset: QuerySet[ActivityRemittance]):
        for remittance in queryset:
            remittance.activityreceipt_set.update(state=State.SEND)

            message_vars = {'num_receipts': remittance.activityreceipt_set.count(), 'remittance': str(remittance)}
            message = gettext_lazy("%(num_receipts)s receipts set as sent for remittance %(remittance)s") % message_vars
            self.message_user(request=request, message=message)

    @admin.action(description=gettext_lazy("Set all receipts as paid"))
    def set_all_receipts_as_paid(self, request, queryset: QuerySet[ActivityRemittance]):
        for remittance in queryset:
            remittance.activityreceipt_set.update(state=State.PAID)

            message_vars = {'num_receipts': remittance.activityreceipt_set.count(), 'remittance': str(remittance)}
            message = gettext_lazy("%(num_receipts)s receipts set as paid for remittance %(remittance)s") % message_vars
            self.message_user(request=request, message=message)

    @staticmethod
    def create_csv_response_from_remittance(remittance: Remittance) -> HttpResponse:
        headers = {'Content-Disposition': f'attachment; filename="{remittance.name}.csv"'}
        response = HttpResponse(content_type='text/csv', headers=headers)
        response.write(codecs.BOM_UTF8)
        csv.writer(response, quoting=csv.QUOTE_ALL).writerows(remittance.obtain_rows())
        return response

    @admin.display(description=gettext_lazy('Total receipts'))
    def receipt_count(self, remittance):
        return remittance.activityreceipt_set.count()

    @admin.display(description=gettext_lazy('Created receipts'))
    def receipt_created_count(self, remittance):
        return remittance.get_receipt_count(state=State.CREATED)

    @admin.display(description=gettext_lazy('Sent receipts'))
    def receipt_sent_count(self, remittance):
        return remittance.get_receipt_count(state=State.SEND)

    @admin.display(description=gettext_lazy('Paid receipts'))
    def receipt_paid_count(self, remittance):
        return remittance.get_receipt_count(state=State.PAID)

    actions = [download_csv, set_all_receipts_as_sent, set_all_receipts_as_paid]

