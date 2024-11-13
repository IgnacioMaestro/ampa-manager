from typing import Optional

from django import forms
from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, gettext_lazy

from ampa_manager.activity.admin.custody_edition_filters import CustodyEditionHasRemittanceFilter, \
    CustodyEditionAcademicCourse
from ampa_manager.activity.admin.registration_filters import RegistrationFilter, ChildLevelListFilter, \
    FamilyRegistrationFilter
from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.charge.models.custody.custody_remittance import CustodyRemittance
from ampa_manager.charge.use_cases.custody.custody_remittance_creator.custody_remittance_creator import \
    CustodyRemittanceCreator
from ampa_manager.charge.use_cases.remittance_creator_error import RemittanceCreatorError
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.membership import Membership
from ampa_manager.family.use_cases.family_emails_exporter import FamilyEmailExporter
from ampa_manager.read_only_inline import ReadOnlyTabularInline
from ampa_manager.utils.csv_http_response import CsvHttpResponse
from ampa_manager.utils.utils import Utils


class CustodyRegistrationAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.id:
            self.fields['holder'].queryset = Holder.objects.of_family(self.instance.child.family)
        else:
            self.fields['holder'].queryset = Holder.objects.none()


class CustodyRegistrationAdmin(admin.ModelAdmin):
    list_display = ['custody_edition_short', 'family_surnames', 'child_name', 'holder', 'assisted_days', 'is_member',
                    'price']
    ordering = ['custody_edition']
    list_filter = ['custody_edition__academic_course__initial_year', 'custody_edition__period',
                   'custody_edition__cycle', RegistrationFilter, ChildLevelListFilter, FamilyRegistrationFilter]
    search_fields = ['child__name', 'child__family__surnames', 'holder__bank_account__iban',
                     'holder__parent__name_and_surnames', 'child__id', 'child__family__id']
    list_per_page = 25
    # form = CustodyRegistrationAdminForm

    @admin.display(description=gettext_lazy('Member'))
    def is_member(self, registration):
        return _('Yes') if Membership.is_member_child(registration.child) else _('No')

    @admin.display(description=gettext_lazy('Custody edition'))
    def custody_edition_short(self, registration):
        return registration.custody_edition.str_short()

    @admin.display(description=gettext_lazy('Child'))
    def child_name(self, registration):
        return registration.child.str_short()

    @admin.display(description=gettext_lazy('Family'))
    def family_surnames(self, registration):
        return registration.child.family.surnames

    @admin.display(description=gettext_lazy('Price'))
    def price(self, registration):
        return registration.calculate_price()


class CustodyRegistrationInline(ReadOnlyTabularInline):
    model = CustodyRegistration
    fields = ['custody_edition', 'child', 'is_member', 'holder', 'assisted_days', 'link']
    readonly_fields = fields
    ordering = ['custody_edition', 'child__name', 'child__family__surnames']

    @admin.display(description=gettext_lazy('Is member'), boolean=True)
    def is_member(self, registration):
        return Membership.is_member_child(registration.child)

    @admin.display(description=_('Id'))
    def link(self, registration):
        return registration.get_html_link(True)


class CustodyEditionAdmin(admin.ModelAdmin):
    inlines = [CustodyRegistrationInline]
    list_display = ['academic_course', 'cycle', 'period', 'price_for_member', 'price_for_no_member',
                    'max_days_for_charge', 'days_with_service', 'cost', 'charged', 'members_registrations_count',
                    'no_members_registrations_count', 'registrations_count', 'has_remittance', 'id']
    fieldsets = (
        (None, {
            'fields': ('academic_course', 'cycle', 'period')
        }),
        (_('Prices'), {
            'fields': ('cost', 'days_with_service', 'max_days_for_charge', 'price_for_member', 'price_for_no_member',
                       'charged'),
        }),
        (_('Registrations'), {
            'fields': ('members_registrations_count', 'no_members_registrations_count', 'registrations_count'),
        }),
        (_('Assisted days'), {
            'fields': ('members_assisted_days', 'topped_members_assisted_days', 'no_members_assisted_days',
                       'topped_no_members_assisted_days'),
        }),
        (_('Remittance'), {
            'fields': ('remittance',),
        }),
    )
    readonly_fields = ['remittance', 'members_registrations_count', 'no_members_registrations_count',
                       'registrations_count', 'members_assisted_days', 'topped_members_assisted_days',
                       'no_members_assisted_days', 'topped_no_members_assisted_days', 'charged', 'max_days_for_charge']
    ordering = ['-academic_course', 'cycle', 'period', '-id']
    list_filter = [CustodyEditionAcademicCourse, 'academic_course__initial_year', CustodyEditionHasRemittanceFilter,
                   'period', 'cycle']
    list_per_page = 25

    @admin.display(description=gettext_lazy('Charged'))
    def charged(self, edition):
        return edition.charged

    @admin.display(description=gettext_lazy('Members'))
    def members_assisted_days(self, edition):
        return edition.get_assisted_days(members=True, topped=False)

    @admin.display(description=gettext_lazy('Members (topped by "Max days for charge")'))
    def topped_members_assisted_days(self, edition):
        return edition.get_assisted_days(members=True, topped=True)

    @admin.display(description=gettext_lazy('No members'))
    def no_members_assisted_days(self, edition):
        return edition.get_assisted_days(members=False, topped=False)

    @admin.display(description=gettext_lazy('No members (topped by "Max days for charge")'))
    def topped_no_members_assisted_days(self, edition):
        return edition.get_assisted_days(members=False, topped=True)

    @admin.display(description=gettext_lazy('No members'))
    def no_members_registrations_count(self, edition):
        return edition.no_members_registrations_count

    @admin.display(description=gettext_lazy('Members'))
    def members_registrations_count(self, edition):
        return edition.members_registrations_count

    @admin.display(description=gettext_lazy('Total'))
    def registrations_count(self, edition):
        return edition.registrations_count

    @admin.display(description=gettext_lazy('Remittance'))
    def remittance(self, edition):
        remittances = CustodyRemittance.objects.filter(custody_editions=edition)
        if remittances.count() == 1:
            return str(remittances.first())
        elif remittances.count() == 0:
            return '-'
        else:
            return _('Multiple remmitances')

    @admin.display(description=gettext_lazy('Remittance'), boolean=True)
    def has_remittance(self, edition):
        remittances = CustodyRemittance.objects.filter(custody_editions=edition)
        return remittances.exists()

    @admin.action(description=_("Create custody remittance"))
    def create_custody_remittance(self, request, custody_editions: QuerySet[CustodyEdition]):
        custody_remittance: Optional[CustodyRemittance]
        error: Optional[RemittanceCreatorError]
        custody_remittance, error = CustodyRemittanceCreator(custody_editions).create()
        if error == RemittanceCreatorError.BIC_ERROR:
            message = Utils.create_bic_error_message()
            return self.message_user(request=request, message=message, level=messages.ERROR)
        url = custody_remittance.get_admin_url()
        message = mark_safe(
            _("Activity remittance created") + " (<a href=\"" + url + "\">" + _("View details") + "</a>)")
        return self.message_user(request=request, message=message)
    
    @admin.action(description=_("Calculate prices based on cost and registrations"))
    def calculate_prices(self, request, editions: QuerySet[CustodyEdition]):
        if not CustodyEdition.are_ready_to_calculate_prices(editions):
            message = _("Any of the required fields to calculate the price is missing (cost, days with service, registrations)")
            return self.message_user(request=request, message=message)

        CustodyEdition.calculate_prices_from_multiple_editions(editions)
        edition = editions.first()
        message = _("Editions' prices calculated")
        message += '. ' + _('Members') + f': {round(edition.price_for_member, 2)}€'
        message += '. ' + _('Non members') + f': {round(edition.price_for_no_member, 2)}€'
        return self.message_user(request=request, message=message)

    @admin.action(description=gettext_lazy("Export family emails to CSV"))
    def download_families_emails(self, request, editions: QuerySet[CustodyEdition]):
        families = []
        for edition in editions.all():
            for registration in edition.registrations.all():
                families.append(registration.child.family)
        emails_csv = FamilyEmailExporter(families).export_to_csv()
        return CsvHttpResponse('correos.csv', emails_csv)

    actions = [create_custody_remittance, calculate_prices, download_families_emails]
