# from ampa_manager.charge.use_cases.custody.custody_remittance_creator.custody_remittance_creator import \
#     CustodyRemittanceCreator
from django.contrib import admin
from django.db.models import QuerySet
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.charge.use_cases.custody.custody_remittance_creator.custody_remittance_creator import \
    CustodyRemittanceCreator
from ampa_manager.read_only_inline import ReadOnlyTabularInline


class CustodyRegistrationAdmin(admin.ModelAdmin):
    list_display = ['custody_edition', 'child', 'holder']
    ordering = ['custody_edition']
    list_filter = ['custody_edition__academic_course__initial_year', 'custody_edition__period',
                   'custody_edition__levels']
    search_fields = ['child__name', 'child__family__surnames', 'holder__bank_account__iban',
                     'holder__parent__name_and_surnames']
    list_per_page = 25


class CustodyRegistrationInline(ReadOnlyTabularInline):
    model = CustodyRegistration
    list_display = ['custody_edition', 'child', 'holder']
    ordering = ['custody_edition']
    extra = 0


class CustodyEditionAdmin(admin.ModelAdmin):
    inlines = [CustodyRegistrationInline]
    list_display = ['academic_course', 'period', 'cycle', 'price_for_member', 'price_for_no_member']
    ordering = ['-academic_course']
    list_filter = ['academic_course__initial_year']
    list_per_page = 25

    @admin.action(description=_("Create custody remittance"))
    def create_custody_remittance(self, request, custody_editions: QuerySet[CustodyEdition]):
        custody_remittance = CustodyRemittanceCreator(custody_editions).create()
        url = custody_remittance.get_admin_url()
        message = mark_safe(
            _("Activity remittance created") + " (<a href=\"" + url + "\">" + _("View details") + "</a>)")
        return self.message_user(request=request, message=message)

    actions = [create_custody_remittance]
