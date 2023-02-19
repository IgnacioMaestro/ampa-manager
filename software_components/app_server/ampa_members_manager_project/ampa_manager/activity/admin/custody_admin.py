# from ampa_manager.charge.use_cases.custody.custody_remittance_creator.custody_remittance_creator import \
#     CustodyRemittanceCreator
from django.contrib import admin
from django.db.models import QuerySet
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, gettext_lazy

from ampa_manager.activity.admin.custody_edition_filters import CustodyEditionHasRemittanceFilter
from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.charge.models.custody.custody_remittance import CustodyRemittance
from ampa_manager.charge.use_cases.custody.custody_remittance_creator.custody_remittance_creator import \
    CustodyRemittanceCreator
from ampa_manager.read_only_inline import ReadOnlyTabularInline


class CustodyRegistrationAdmin(admin.ModelAdmin):
    list_display = ['custody_edition', 'child', 'holder', 'assisted_days']
    ordering = ['custody_edition']
    list_filter = ['custody_edition__academic_course__initial_year', 'custody_edition__period',
                   'custody_edition__levels']
    search_fields = ['child__name', 'child__family__surnames', 'holder__bank_account__iban',
                     'holder__parent__name_and_surnames']
    list_per_page = 25


class CustodyRegistrationInline(ReadOnlyTabularInline):
    model = CustodyRegistration
    list_display = ['custody_edition', 'child', 'holder', 'assisted_days']
    ordering = ['custody_edition']
    extra = 0


class CustodyEditionAdmin(admin.ModelAdmin):
    inlines = [CustodyRegistrationInline]
    list_display = ['academic_course', 'cycle', 'period', 'price_for_member', 'price_for_no_member',
                    'max_days_for_charge', 'registrations_count', 'remittance']
    fields = ['academic_course', 'cycle', 'period', 'price_for_member', 'price_for_no_member', 'max_days_for_charge']
    ordering = ['-academic_course', 'cycle', '-id']
    list_filter = ['academic_course__initial_year', CustodyEditionHasRemittanceFilter, 'period', 'cycle']
    list_per_page = 25

    @admin.display(description=gettext_lazy('Registrations'))
    def registrations_count(self, edition):
        return CustodyRegistration.objects.of_edition(edition).count()

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
        
        message = _("%(calculated)s editions' prices calculated") % {'calculated': calculated}
        if not_calculated:
            message += '. ' + _("Unable to calculate %(not_calculated)s editions' prices") % {'not_calculated': not_calculated}
        message += '. ' + _("Prices calculated based on edition cost and number of registrations")

        return self.message_user(request=request, message=message)

    actions = [create_custody_remittance, calculate_prices]
