from django import forms
from django.contrib import admin
from django.db.models import QuerySet
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, gettext_lazy

from ampa_manager.activity.admin.custody_edition_filters import CustodyEditionHasRemittanceFilter, \
    CustodyEditionAcademicCourse
from ampa_manager.activity.admin.registration_filters import RegistrationFilter, ChildLevelListFilter
from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.charge.models.custody.custody_remittance import CustodyRemittance
from ampa_manager.charge.use_cases.custody.custody_remittance_creator.custody_remittance_creator import \
    CustodyRemittanceCreator
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.membership import Membership
from ampa_manager.read_only_inline import ReadOnlyTabularInline


class CustodyRegistrationAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.id:
            self.fields['holder'].queryset = Holder.objects.of_family(self.instance.child.family)
        else:
            self.fields['holder'].queryset = Holder.objects.none()


class CustodyRegistrationAdmin(admin.ModelAdmin):
    list_display = ['custody_edition', 'child', 'holder', 'assisted_days', 'is_member']
    ordering = ['custody_edition']
    list_filter = ['custody_edition__academic_course__initial_year', 'custody_edition__period',
                   'custody_edition__cycle', RegistrationFilter, ChildLevelListFilter]
    search_fields = ['child__name', 'child__family__surnames', 'holder__bank_account__iban',
                     'holder__parent__name_and_surnames', 'child__id']
    list_per_page = 25
    # form = CustodyRegistrationAdminForm

    @admin.display(description=gettext_lazy('Is member'))
    def is_member(self, registration):
        return _('Yes') if Membership.is_member_child(registration.child) else _('No')


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
                    'max_days_for_charge', 'cost', 'charged', 'members_registrations_count',
                    'no_members_registrations_count', 'registrations_count', 'has_remittance', 'id']
    fieldsets = (
        (None, {
            'fields': ('academic_course', 'cycle', 'period')
        }),
        (_('Prices'), {
            'fields': ('cost', 'max_days_for_charge', 'price_for_member', 'price_for_no_member', 'charged'),
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
                       'no_members_assisted_days', 'topped_no_members_assisted_days', 'charged']
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
        custody_remittance = CustodyRemittanceCreator(custody_editions).create()
        url = custody_remittance.get_admin_url()
        message = mark_safe(
            _("Activity remittance created") + " (<a href=\"" + url + "\">" + _("View details") + "</a>)")
        return self.message_user(request=request, message=message)
    
    @admin.action(description=_("Calculate prices"))
    def calculate_prices(self, request, custody_editions: QuerySet[CustodyEdition]):
        calculated = 0
        not_calculated = 0
        for edition in custody_editions:
            if edition.calculate_prices():
                calculated += 1
            else:
                not_calculated += 1

        message = ''
        if calculated:
            message = _("%(calculated)s editions' prices calculated") % {'calculated': calculated}
        if not_calculated:
            if message:
                message += '. '
            message += _("Unable to calculate %(not_calculated)s editions' prices") % {'not_calculated': not_calculated}
        message += '. ' + _("Prices calculated based on edition cost and number of registrations")

        return self.message_user(request=request, message=message)

    @admin.action(description=gettext_lazy("Export family emails to CSV"))
    def export_emails(self, request, custody_editions: QuerySet[CustodyEdition]):
        emails = []
        for custody_edition in custody_editions.all():
            for custody_registration in custody_edition.registrations.all():
                for email in custody_registration.child.family.get_parents_emails():
                    if email not in emails:
                        emails.append(email)

        emails_csv = ",".join(emails)
        headers = {'Content-Disposition': f'attachment; filename="correos.csv"'}
        return HttpResponse(content_type='text/csv', headers=headers, content=emails_csv)

    actions = [create_custody_remittance, calculate_prices, export_emails]
