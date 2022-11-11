from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.family.admin.filters.parent_filters import ParentFamilyEmailsFilter, ParentFamiliesCountFilter
from ampa_members_manager.family.models.bank_account.bank_account import BankAccount
from ampa_members_manager.family.models.membership import Membership


class BankAccountInline(admin.TabularInline):
    model = BankAccount
    fields = ['swift_bic', 'iban', 'owner']
    extra = 0


class ParentAdmin(admin.ModelAdmin):
    list_display = ['name_and_surnames', 'parent_families', 'email', 'phone_number', 'additional_phone_number',
                    'is_member']
    fields = ['name_and_surnames', 'phone_number', 'additional_phone_number', 'email', 'created', 'modified']
    readonly_fields = ['created', 'modified']
    ordering = ['name_and_surnames']
    search_fields = ['name_and_surnames', 'family__surnames', 'phone_number', 'additional_phone_number']
    inlines = [BankAccountInline]
    list_per_page = 25
    list_filter = [ParentFamilyEmailsFilter, ParentFamiliesCountFilter]

    @admin.display(description=_('Is member'))
    def is_member(self, parent):
        return _('Yes') if Membership.objects.of_parent(parent).exists() else _('No')

    @admin.display(description=_('Family'))
    def parent_families(self, parent):
        return ', '.join(str(f) for f in parent.family_set.all())
