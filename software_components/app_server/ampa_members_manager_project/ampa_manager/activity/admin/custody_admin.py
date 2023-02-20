# from ampa_manager.charge.use_cases.custody.custody_remittance_creator.custody_remittance_creator import \
#     CustodyRemittanceCreator
from django.contrib import admin
from django.db.models import QuerySet
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, gettext_lazy

from ampa_manager.activity.admin.custody_edition_filters import CustodyEditionHasRemittanceFilter
from ampa_manager.activity.admin.custody_registration_filters import CustodyRegistrationFilter, ChildLevelListFilter
from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.charge.models.custody.custody_remittance import CustodyRemittance
from ampa_manager.charge.use_cases.custody.custody_remittance_creator.custody_remittance_creator import \
    CustodyRemittanceCreator
from ampa_manager.family.models.membership import Membership
from ampa_manager.read_only_inline import ReadOnlyTabularInline


class CustodyRegistrationAdmin(admin.ModelAdmin):
    list_display = ['custody_edition', 'child', 'holder', 'assisted_days', 'is_member']
    ordering = ['custody_edition']
    list_filter = ['custody_edition__academic_course__initial_year', 'custody_edition__period',
                   'custody_edition__cycle', CustodyRegistrationFilter, ChildLevelListFilter]
    search_fields = ['child__name', 'child__family__surnames', 'holder__bank_account__iban',
                     'holder__parent__name_and_surnames']
    list_per_page = 25

    @admin.display(description=gettext_lazy('Is member'))
    def is_member(self, registration):
        return _('Yes') if Membership.is_member_child(registration.child) else _('No')


class CustodyRegistrationInline(ReadOnlyTabularInline):
    model = CustodyRegistration
    list_display = ['custody_edition', 'child', 'holder', 'assisted_days']
    ordering = ['custody_edition']
    extra = 0


class CustodyEditionAdmin(admin.ModelAdmin):
    inlines = [CustodyRegistrationInline]
    list_display = ['academic_course', 'cycle', 'period', 'price_for_member', 'price_for_no_member',
                    'max_days_for_charge', 'cost', 'members_registrations_count', 'no_members_registrations_count',
                    'registrations_count', 'remittance']
    fieldsets = (
        (None, {
            'fields': ('academic_course', 'cycle', 'period')
        }),
        (_('Prices'), {
            'fields': ('cost', 'max_days_for_charge', 'price_for_member', 'price_for_no_member'),
        }),
        (_('Registrations'), {
            'fields': ('members_registrations_count', 'no_members_registrations_count', 'registrations_count'),
        }),
        (_('Assisted days'), {
            'fields': ('members_assisted_days', 'topped_members_assisted_days', 'no_members_assisted_days',
                       'topped_no_members_assisted_days'),
        }),
        (_('Remmitance'), {
            'fields': ('remittance',),
        }),
    )
    readonly_fields = ['remittance', 'members_registrations_count', 'no_members_registrations_count',
                       'registrations_count', 'members_assisted_days', 'topped_members_assisted_days',
                       'no_members_assisted_days', 'topped_no_members_assisted_days']
    ordering = ['-academic_course', 'cycle', '-id']
    list_filter = ['academic_course__initial_year', CustodyEditionHasRemittanceFilter, 'period', 'cycle']
    list_per_page = 25

    @admin.display(description=gettext_lazy('Members'))
    def members_assisted_days(self, edition):
        return edition.get_assisted_days(members=True, topped=False)

    @admin.display(description=gettext_lazy('Members (topped)'))
    def topped_members_assisted_days(self, edition):
        return edition.get_assisted_days(members=True, topped=True)

    @admin.display(description=gettext_lazy('No members'))
    def no_members_assisted_days(self, edition):
        return edition.get_assisted_days(members=False, topped=False)

    @admin.display(description=gettext_lazy('No members (topped)'))
    def topped_no_members_assisted_days(self, edition):
        return edition.get_assisted_days(members=False, topped=True)

    @admin.display(description=gettext_lazy('No members'))
    def no_members_assisted_days(self, edition):
        return edition.no_members_registrations_count

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

    actions = [create_custody_remittance, calculate_prices]
