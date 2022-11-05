import csv
import codecs

from django import forms
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.academic_course.models.academic_course import AcademicCourse
from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.academic_course.models.level import Level
from ampa_members_manager.charge.admin import MembershipReceiptInline
from ampa_members_manager.charge.models.activity_receipt import ActivityReceipt
from ampa_members_manager.charge.use_cases.create_membership_remittance_with_families.membership_remittance_creator import \
    MembershipRemittanceCreator
from ampa_members_manager.family.filters.bank_account_filters import BankAccountAuthorizationFilter, BankAccountBICCodeFilter
from ampa_members_manager.family.filters.child_filters import ChildLevelListFilter, ChildCycleFilter
from ampa_members_manager.family.filters.family_filters import FamilyIsMemberFilter, FamilyChildrenCountFilter, \
    FamilyDefaultAccountFilter, FamilyParentCountFilter
from ampa_members_manager.family.filters.parent_filters import ParentFamilyEmailsFilter, ParentFamiliesCountFilter
from ampa_members_manager.family.models.authorization.authorization import Authorization
from ampa_members_manager.family.models.bank_account.bank_account import BankAccount
from ampa_members_manager.family.models.child import Child
from ampa_members_manager.family.models.family import Family
from ampa_members_manager.family.models.membership import Membership
from ampa_members_manager.family.models.state import State
from ampa_members_manager.non_related_inlines import NonrelatedTabularInline
from ampa_members_manager.read_only_inline import ReadOnlyTabularInline


class FamilyAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['default_bank_account'].queryset = BankAccount.objects.of_family(self.instance)
        else:
            self.fields['default_bank_account'].queryset = BankAccount.objects.none()


class ChildInline(admin.TabularInline):
    model = Child
    extra = 0


class MembershipInline(ReadOnlyTabularInline):
    model = Membership
    extra = 0


class FamilyActivityReceiptInline(NonrelatedTabularInline):
    model = ActivityReceipt
    fields = ['amount', 'state']

    def get_form_queryset(self, family):
        return ActivityReceipt.objects.of_family(family)


class FamilyAdmin(admin.ModelAdmin):
    list_display = ['surnames', 'email', 'secondary_email', 'default_bank_account', 'parent_count',
                    'children_in_school_count', 'is_member', 'created_formatted']
    fields = ['surnames', 'parents', 'email', 'secondary_email', 'default_bank_account', 'decline_membership', 'is_defaulter',
              'created', 'modified']
    readonly_fields = ['created', 'modified']
    ordering = ['surnames']
    list_filter = [FamilyIsMemberFilter, FamilyChildrenCountFilter, FamilyDefaultAccountFilter, 'created', 'modified',
                   'is_defaulter', 'decline_membership', FamilyParentCountFilter]
    search_fields = ['surnames', 'email', 'secondary_email']
    form = FamilyAdminForm
    filter_horizontal = ['parents']
    inlines = [ChildInline, MembershipInline, MembershipReceiptInline, FamilyActivityReceiptInline]
    list_per_page = 25

    @admin.action(description=_("Generate MembershipRemittance for current year"))
    def generate_remittance(self, request, families: QuerySet[Family]):
        academic_course: AcademicCourse = ActiveCourse.load()
        remittance = MembershipRemittanceCreator(families, academic_course).create()
        message = mark_safe(
            _("Membership remittance created") + " (<a href=\"" + remittance.get_admin_url() + "\">" + _(
                "View details") + "</a>)")
        return self.message_user(request=request, message=message)

    @admin.action(description=_("Export emails to CSV"))
    def export_emails(self, request, families: QuerySet[Family]):
        emails = []
        for family in families:
            if family.email and family.email not in emails:
                emails.append(family.email)
            if family.secondary_email and family.secondary_email not in emails:
                emails.append(family.secondary_email)

        headers = {'Content-Disposition': f'attachment; filename="emails.csv"'}
        return HttpResponse(content_type='text/csv', headers=headers, content=",".join(emails))

    @admin.action(description=_("Make families member"))
    def make_members(self, request, families: QuerySet[Family]):
        new_members = 0
        already_members = 0
        declined = 0
        for family in families:
            if Membership.is_member_family(family):
                already_members += 1
            elif family.decline_membership:
                declined += 1
            else:
                Membership.make_member_for_active_course(family)
                new_members += 1

        message = _(
            '%(new_members)s families became members. %(already_members)s families already were members. %(declined)s families declined to be members anymore') % {
                      'new_members': new_members, 'already_members': already_members, 'declined': declined}
        return self.message_user(request=request, message=message)

    @admin.display(description=_('Parents'))
    def parent_count(self, family):
        return family.get_parent_count()

    @admin.display(description=_('Children'))
    def children_count(self, family):
        return family.get_children_count()

    @admin.display(description=_('In school'))
    def children_in_school_count(self, family):
        return f'{family.get_children_in_school_count()}/{family.get_children_count()}'

    @admin.display(description=_('Is member'))
    def is_member(self, family):
        return _('Yes') if Membership.is_member_family(family) else _('No')

    @admin.display(description=_('Created'))
    def created_formatted(self, family):
        return family.created.strftime('%d/%m/%y, %H:%M')

    created_formatted.admin_order_field = 'created'

    actions = [generate_remittance, export_emails, make_members]


class BankAccountInline(admin.TabularInline):
    model = BankAccount
    fields = ['swift_bic', 'iban', 'owner']
    extra = 0


class ParentAdmin(admin.ModelAdmin):
    # list_display = ['name_and_surnames', 'parent_families', 'email', 'phone_number', 'additional_phone_number', 'is_member']
    list_display = ['name_and_surnames', 'email', 'family_email1', 'family_email2', 'parent_families']
    fields = ['name_and_surnames', 'phone_number', 'additional_phone_number', 'email', 'created', 'modified']
    readonly_fields = ['created', 'modified']
    ordering = ['name_and_surnames']
    search_fields = ['name_and_surnames', 'family__surnames', 'phone_number', 'additional_phone_number']
    inlines = [BankAccountInline]
    list_per_page = 25
    list_filter = [ParentFamilyEmailsFilter, ParentFamiliesCountFilter]

    @admin.display(description=_('Is member'))
    def is_member(self, parent):
        return _('Yes') if Membership.objects.by_parent(parent).exists() else _('No')

    @admin.display(description=_('Family'))
    def parent_families(self, parent):
        return ', '.join(str(f) for f in parent.family_set.all())
    
    @admin.display(description=_('Family email 1'))
    def family_email1(self, parent):
        if parent.family_set.count() == 1:
            return parent.family_set.first().email
        else:
            return None

    @admin.display(description=_('Family email 2'))
    def family_email2(self, parent):
        if parent.family_set.count() == 1:
            return parent.family_set.first().secondary_email
        else:
            return None
    
    @admin.action(description=_("Delete family emails"))
    def delete_family_emails(self, request, queryset: QuerySet[Authorization]):
        for parent in queryset:
            for family in parent.family_set.all():
                if family.email or family.secondary_email:
                    family.email = None
                    family.secondary_email = None
                    family.save()
    
    @admin.action(description=_("Import email from family email 1"))
    def import_family_email1(self, request, queryset: QuerySet[Authorization]):
        for parent in queryset:
            if parent.family_set.count() == 1:
                family = parent.family_set.first()
                if family.email and not parent.email:
                    parent.email = family.email
                parent.save()
    
    @admin.action(description=_("Import email from family email 2"))
    def import_family_email2(self, request, queryset: QuerySet[Authorization]):
        for parent in queryset:
            if parent.family_set.count() == 1:
                family = parent.family_set.first()
                if family.secondary_email and not parent.email:
                    parent.email = family.secondary_email
                parent.save()
    
    @admin.action(description=_("Import family email if there is only one"))
    def try_to_complete_email(self, request, queryset: QuerySet[Authorization]):
        for parent in queryset:
            if parent.email in ['', None]:
                if parent.family_set.count() == 1:
                    family = parent.family_set.first()
                    emails = []
                    if family.email:
                        emails.append(family.email)
                    if family.secondary_email:
                        emails.append(family.secondary_email)
                    if len(emails) == 1:
                        parent.email = emails[0]
                        parent.save()
    
    actions = ['delete_family_emails', 'import_family_email1', 'import_family_email2', 'try_to_complete_email']


class ChildAdmin(admin.ModelAdmin):
    list_display = ['name', 'family', 'parents', 'year_of_birth', 'repetition', 'child_course', 'is_member']
    fields = ['name', 'family', 'year_of_birth', 'repetition', 'created', 'modified']
    readonly_fields = ['created', 'modified']
    ordering = ['name']
    list_filter = [ChildCycleFilter, ChildLevelListFilter, 'year_of_birth', 'repetition']
    search_fields = ['name', 'year_of_birth', 'family__surnames']
    list_per_page = 25

    @admin.display(description=_('Is member'))
    def is_member(self, child):
        return _('Yes') if Membership.is_member_child(child) else _('No')

    @admin.display(description=_('Course'))
    def child_course(self, child):
        return Level.get_level_name(child.level)

    @admin.display(description=_('Parents'))
    def parents(self, child):
        return ', '.join(p.name_and_surnames for p in child.family.parents.all())


class AuthorizationInline(admin.TabularInline):
    model = Authorization
    extra = 0


class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['owner', 'iban', 'swift_bic', 'authorization_status']
    fields = ['owner', 'iban', 'swift_bic', 'created', 'modified']
    readonly_fields = ['created', 'modified']
    ordering = ['owner__name_and_surnames']
    list_filter = [BankAccountAuthorizationFilter, BankAccountBICCodeFilter]
    search_fields = ['swift_bic', 'iban', 'owner__name_and_surnames']
    inlines = [AuthorizationInline]
    list_per_page = 25

    @admin.display(description=_('Authorization'))
    def authorization_status(self, bank_account):
        try:
            authorization = Authorization.objects.of_bank_account(bank_account).get()
            return State.get_value_human_name(authorization.state)
        except Authorization.DoesNotExist:
            return _('No authorizacion')
    
    @admin.action(description=_("Export account owners"))
    def export_owners(self, request, bank_accounts: QuerySet[BankAccount]):
        file_name = _('Bank account owners').lower()
        headers = {'Content-Disposition': f'attachment; filename="{file_name}.csv"'}
        response = HttpResponse(content_type='text/csv', headers=headers)
        response.write(codecs.BOM_UTF8)
        csv.writer(response, quoting=csv.QUOTE_ALL).writerows(BankAccount.get_csv_fields(bank_accounts))
        return response
    
    @admin.action(description=_("Complete SWIFT/BIC codes"))
    def complete_swift_bic(self, request, bank_accounts: QuerySet[BankAccount]):
        for bank_account in bank_accounts:
            if bank_account.swift_bic in [None, '']:
                bank_account.complete_swift_bic()
                bank_account.save()
    
    actions = ['export_owners', 'complete_swift_bic']


class AuthorizationAdmin(admin.ModelAdmin):
    list_display = ['number', 'year', 'date', 'bank_account', 'document', 'state']
    ordering = ['-date']
    list_filter = ['year', 'state']
    search_fields = ['number', 'year', 'date', 'bank_account__iban', 'bank_account__owner__name_and_surnames']
    list_per_page = 25

    @admin.action(description=_("Set as not sent"))
    def set_as_not_sent(self, request, queryset: QuerySet[Authorization]):
        queryset.update(state=State.NOT_SENT)

        message = _("%(num_authorizations)s authorizations set as NOT sent") % {'num_authorizations': queryset.count()}
        self.message_user(request=request, message=message)

    @admin.action(description=_("Set as sent"))
    def set_as_sent(self, request, queryset: QuerySet[Authorization]):
        queryset.update(state=State.SENT)

        message = _("%(num_authorizations)s authorizations set as sent") % {'num_authorizations': queryset.count()}
        self.message_user(request=request, message=message)

    @admin.action(description=_("Set as signed"))
    def set_as_signed(self, request, queryset: QuerySet[Authorization]):
        queryset.update(state=State.SIGNED)

        message = _("%(num_authorizations)s authorizations set as signed") % {'num_authorizations': queryset.count()}
        self.message_user(request=request, message=message)

    actions = [set_as_not_sent, set_as_sent, set_as_signed]


class MembershipAdmin(admin.ModelAdmin):
    list_display = ['family', 'academic_course']
    ordering = ['-academic_course', 'family__surnames']
    list_filter = ['academic_course__initial_year']
    search_fields = ['family__surnames', 'academic_course__initial_year']
    list_per_page = 25
