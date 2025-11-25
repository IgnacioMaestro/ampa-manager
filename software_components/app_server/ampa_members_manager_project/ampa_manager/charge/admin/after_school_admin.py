import locale
from typing import Optional

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy
from django.utils.translation import gettext_lazy as _

from ampa_manager.read_only_inline import ReadOnlyTabularInline
from . import ERROR_REMITTANCE_NOT_FILLED, ERROR_ONLY_ONE_REMITTANCE
from .filters.receipt_filters import FamilyReceiptFilter, AfterSchoolEditionReceiptFilter, ParentReceiptFilter
from ..models.after_school_charge.after_school_receipt import AfterSchoolReceipt
from ..models.after_school_charge.after_school_remittance import AfterSchoolRemittance
from ..remittance import Remittance
from ..remittance_utils import RemittanceUtils
from ..sepa.sepa_response_creator import SEPAResponseCreator
from ..use_cases.after_school.remittance_generator_from_after_school_remittance import \
    RemittanceGeneratorFromAfterSchoolRemittance
from ..use_cases.remittance_creator_error import RemittanceCreatorError
from ...academic_course.models.academic_course import AcademicCourse
from ...family.models.membership import Membership
from ...family.use_cases.family_emails_exporter import FamilyEmailExporter
from ...utils.csv_http_response import CsvHttpResponse
from ...utils.currency_utils import CurrencyUtils
from ...utils.utils import Utils


class AfterSchoolReceiptAdmin(admin.ModelAdmin):
    list_display = ['remittance', 'edition', 'child', 'holder', 'rounded_amount', 'is_member']
    search_fields = [
        'id',
        'after_school_registration__child__family__surnames',
        'after_school_registration__child__family__id',
        'after_school_registration__child__name',
        'after_school_registration__holder__bank_account__iban',
        'after_school_registration__child__family__parents__name_and_surnames'
    ]
    list_filter = [
        FamilyReceiptFilter, ParentReceiptFilter, AfterSchoolEditionReceiptFilter,
        'after_school_registration__after_school_edition__academic_course__initial_year']
    list_per_page = 25
    autocomplete_fields = ['after_school_registration', 'remittance']

    @admin.display(description=_('Edition'))
    def edition(self, receipt):
        return f'{receipt.after_school_registration.after_school_edition.academic_course}, '\
               f'{receipt.after_school_registration.after_school_edition.after_school}, '\
               f'{receipt.after_school_registration.after_school_edition.period}, '\
               f'{receipt.after_school_registration.after_school_edition.timetable}'

    @admin.display(description=_('Member'), boolean=True)
    def is_member(self, receipt):
        return Membership.is_member_child(receipt.after_school_registration.child)

    @admin.display(description=_('Child'))
    def child(self, receipt):
        child_name = receipt.after_school_registration.child.name
        child_last_names = receipt.after_school_registration.child.family.surnames
        return f'{child_name} {child_last_names}'

    @admin.display(description=gettext_lazy('Holder'))
    def holder(self, receipt):
        return receipt.after_school_registration.holder

    @admin.display(description=gettext_lazy('Total'))
    def rounded_amount(self, receipt):
        return CurrencyUtils.get_rounded_amount(receipt.amount)


class AfterSchoolReceiptInline(ReadOnlyTabularInline):
    model = AfterSchoolReceipt
    extra = 0


class AfterSchoolRemittanceAdmin(admin.ModelAdmin):
    list_display = ['name', 'sepa_id', 'created_at', 'payment_date', 'receipts_total', 'receipts_count', 'courses']
    fields = ['name', 'concept', 'sepa_id', 'created_at', 'payment_date', 'receipts_total', 'receipts_link']
    readonly_fields = ['receipts_link', 'created_at', 'receipts_total', 'sepa_id']
    ordering = ['-created_at']
    list_per_page = 25
    search_fields = ['name', 'concept', 'sepa_id']

    @admin.display(description=gettext_lazy('Course'))
    def courses(self, remittance):
        courses_ids = []
        for edition in remittance.after_school_editions.all():
            if edition.academic_course.id not in courses_ids:
                courses_ids.append(edition.academic_course.id)
        return ', '.join([str(course) for course in AcademicCourse.objects.filter(id__in=courses_ids)])

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

    @admin.action(description=gettext_lazy("Export family emails to CSV"))
    def download_families_emails(self, request, remittances: QuerySet[AfterSchoolRemittance]):
        families = []
        for remittance in remittances.all():
            receipt: AfterSchoolReceipt
            for receipt in remittance.receipts.all():
                families.append(receipt.after_school_registration.child.family)
        emails_csv = FamilyEmailExporter(families).export_to_csv()
        return CsvHttpResponse('correos.csv', emails_csv)

    actions = [download_membership_remittance_sepa_file, download_families_emails]
