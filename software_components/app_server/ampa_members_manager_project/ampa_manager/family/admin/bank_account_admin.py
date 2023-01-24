import codecs
import csv

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.translation import gettext_lazy

from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.family.admin.filters.bank_account_filters import BankAccountAuthorizationFilter, \
    BankAccountBICCodeFilter
from ampa_manager.family.models.authorization.authorization_old import AuthorizationOld
from ampa_manager.family.models.bank_account.bank_account import BankAccount


class AuthorizationInline(admin.TabularInline):
    model = AuthorizationOld
    extra = 0


class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['iban', 'swift_bic']
    fields = ['iban', 'swift_bic', 'created', 'modified']
    readonly_fields = ['created', 'modified']
    list_filter = [BankAccountAuthorizationFilter, BankAccountBICCodeFilter]
    search_fields = ['swift_bic', 'iban']
    inlines = [AuthorizationInline]
    list_per_page = 25

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
            AuthorizationOld.objects.create_next_authorization(year=year, bank_account=bank_account)

    actions = ['export_owners', 'complete_swift_bic', 'create_authorization_for_this_year']
