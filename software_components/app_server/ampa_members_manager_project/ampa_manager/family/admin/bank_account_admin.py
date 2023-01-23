import codecs
import csv

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.translation import gettext_lazy

from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.activity.models.after_school.after_school import AfterSchool
from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.family.admin.filters.bank_account_filters import BankAccountAuthorizationFilter, \
    BankAccountBICCodeFilter
from ampa_manager.family.models.authorization.authorization import Authorization
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.bank_account.iban import IBAN
from ampa_manager.family.models.state import State
from django.utils.translation import gettext_lazy as _

from ampa_manager.read_only_inline import ReadOnlyTabularInline


class AuthorizationInline(admin.TabularInline):
    model = Authorization
    extra = 0

class AfterSchoolRegistrationInline(ReadOnlyTabularInline):
    model = AfterSchoolRegistration


class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['owner', 'iban', 'swift_bic', 'authorization_status', 'after_school_count']
    fields = ['owner', 'iban', 'swift_bic', 'created', 'modified']
    readonly_fields = ['created', 'modified']
    ordering = ['owner__name_and_surnames']
    list_filter = [BankAccountAuthorizationFilter, BankAccountBICCodeFilter]
    search_fields = ['swift_bic', 'iban', 'owner__name_and_surnames']
    inlines = [AuthorizationInline, AfterSchoolRegistrationInline]
    list_per_page = 25

    @admin.display(description=gettext_lazy('After schools'))
    def after_school_count(self, bank_account):
        return AfterSchoolRegistration.objects.filter(bank_account=bank_account).count()

    @admin.display(description=gettext_lazy('Authorization'))
    def authorization_status(self, bank_account):
        try:
            authorization = Authorization.objects.of_bank_account(bank_account).get()
            return State.get_value_human_name(authorization.state)
        except Authorization.DoesNotExist:
            return gettext_lazy('No authorization')

    @admin.action(description=gettext_lazy("Export account owners"))
    def export_owners(self, _, bank_accounts: QuerySet[BankAccount]):
        file_name = gettext_lazy('Bank account owners').lower()
        headers = {'Content-Disposition': f'attachment; filename="{file_name}.csv"'}
        response = HttpResponse(content_type='text/csv', headers=headers)
        response.write(codecs.BOM_UTF8)
        csv.writer(response, quoting=csv.QUOTE_ALL).writerows(BankAccount.get_csv_fields(bank_accounts))
        return response

    @admin.action(description=gettext_lazy("Complete SWIFT/BIC codes"))
    def complete_swift_bic(self, _, bank_accounts: QuerySet[BankAccount]):
        for bank_account in bank_accounts.iterator():
            if bank_account.swift_bic in [None, '']:
                bank_account.complete_swift_bic()
                bank_account.save()

    @admin.action(description=gettext_lazy("Create authorization for this year"))
    def create_authorization_for_this_year(self, _, bank_accounts: QuerySet[BankAccount]):
        year = ActiveCourse.load().initial_year
        for bank_account in bank_accounts.iterator():
            Authorization.objects.create_next_authorization(year=year, bank_account=bank_account)

    @admin.action(description=gettext_lazy("Validate IBAN"))
    def validate_iban(self, request, bank_accounts: QuerySet[BankAccount]):
        not_valid_bank_accounts = []
        for bank_account in bank_accounts.iterator():
            if not IBAN.is_valid(str(bank_account.iban)):
                not_valid_bank_accounts.append(str(bank_account.iban))

        if len(not_valid_bank_accounts) == 0:
            return self.message_user(request=request, message=_('All validated IBANs are valid'))
        else:
            return self.message_user(request=request, message=_('%(number)s IBANs are invalid: %(ibans)s') %
                                                              {'number': len(not_valid_bank_accounts),
                                                               'ibans': ', '.join(not_valid_bank_accounts)})

    actions = ['export_owners', 'complete_swift_bic', 'create_authorization_for_this_year', 'validate_iban']
