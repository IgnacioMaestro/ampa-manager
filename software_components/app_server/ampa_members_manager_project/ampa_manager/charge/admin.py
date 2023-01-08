import codecs
import csv
import locale
from typing import List

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy

from ampa_manager.read_only_inline import ReadOnlyTabularInline
from .models.activity_receipt import ActivityReceipt
from .models.activity_remittance import ActivityRemittance
from .models.after_school_charge.after_school_receipt import AfterSchoolReceipt
from .models.after_school_charge.after_school_remittance import AfterSchoolRemittance
from .models.fee.fee import Fee
from .models.membership_receipt import MembershipReceipt
from .models.membership_remittance import MembershipRemittance
from .remittance import Remittance
from .state import State
from .use_cases.activity.generate_remittance_from_activity_remittance.remittance_generator import RemittanceGenerator
from .use_cases.after_school.remittance_generator_from_after_school_remittance import RemittanceGeneratorFromAfterSchoolRemittance
from .use_cases.membership.create_membership_remittance_for_unique_families.membership_remittance_creator_of_active_course import \
    MembershipRemittanceCreatorOfActiveCourse
from .use_cases.membership.generate_remittance_from_membership_remittance.membership_remittance_generator import \
    MembershipRemittanceGenerator

TEXT_CSV = 'text/csv'
RECEIPTS_SET_AS_SENT_MESSAGE = "%(num_receipts)s receipts set as sent"
RECEIPTS_SET_AS_PAID_MESSAGE = "%(num_receipts)s receipts set as paid"


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

        message = gettext_lazy(RECEIPTS_SET_AS_SENT_MESSAGE) % {'num_receipts': queryset.count()}
        self.message_user(request=request, message=message)

    @admin.action(description=gettext_lazy("Set as paid"))
    def set_as_paid(self, request, queryset: QuerySet[ActivityReceipt]):
        queryset.update(state=State.PAID)

        message = gettext_lazy(RECEIPTS_SET_AS_PAID_MESSAGE) % {'num_receipts': queryset.count()}
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
        response = HttpResponse(content_type=TEXT_CSV, headers=headers)
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
        remittance: Remittance = RemittanceGeneratorFromAfterSchoolRemittance(after_school_remittance=queryset.first()).generate()
        return AfterSchoolRemittanceAdmin.create_csv_response_from_remittance(remittance)

    @staticmethod
    def create_csv_response_from_remittance(remittance: Remittance) -> HttpResponse:
        headers = {'Content-Disposition': f'attachment; filename="{remittance.name}"'}
        response = HttpResponse(content_type=TEXT_CSV, headers=headers)
        response.write(codecs.BOM_UTF8)
        rows_to_add: List[List[str]] = [['Titular', 'BIC', 'IBAN', 'Autorizacion', 'Fecha Autorizacion', 'Cantidad']]
        rows_to_add.extend(remittance.obtain_rows())
        csv.writer(response).writerows(rows_to_add)
        return response

    actions = [download_membership_remittance_csv]
