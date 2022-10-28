from django.http import HttpResponse
from django import forms
from django.contrib import admin
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.safestring import mark_safe

from ampa_members_manager.academic_course.models.academic_course import AcademicCourse
from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.charge.use_cases.create_membership_remittance_with_families.membership_remittance_creator import MembershipRemittanceCreator
from ampa_members_manager.family.models.authorization import Authorization
from ampa_members_manager.family.models.bank_account import BankAccount
from ampa_members_manager.family.models.child import Child
from ampa_members_manager.family.models.family import Family
from ampa_members_manager.family.models.membership import Membership
from ampa_members_manager.family.bank_account_filters import BankAccountAuthorizationFilter, BankAccountBICCodeFilter
from ampa_members_manager.family.child_filters import ChildLevelListFilter, ChildCycleFilter
from ampa_members_manager.family.family_filters import FamilyIsMemberFilter, FamilyChildrenCountFilter, FamilyDefaultAccountFilter
from ampa_members_manager.charge.admin import MembershipReceiptInline
from ampa_members_manager.charge.models.activity_receipt import ActivityReceipt
from ampa_members_manager.family.models.state import State
from ampa_members_manager.read_only_inline import ReadOnlyTabularInline
from ampa_members_manager.non_related_inlines import NonrelatedTabularInline


class FamilyAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['default_bank_account'].queryset = BankAccount.objects.by_family(self.instance)
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
        return ActivityReceipt.objects.by_family(family)


class FamilyAdmin(admin.ModelAdmin):
    list_display = ['surnames', 'email', 'secondary_email', 'default_bank_account', 'children_count', 'children_in_school_count', 'is_defaulter', 'is_member']
    fields = ['surnames', 'email', 'secondary_email', 'default_bank_account', 'is_defaulter', 'created', 'modified']
    readonly_fields = ['created', 'modified']
    ordering = ['surnames']
    list_filter = [FamilyIsMemberFilter, FamilyChildrenCountFilter, FamilyDefaultAccountFilter, 'is_defaulter']
    search_fields = ['surnames', 'email', 'secondary_email']
    form = FamilyAdminForm
    filter_horizontal = ['parents']
    inlines = [ChildInline, MembershipInline, MembershipReceiptInline, FamilyActivityReceiptInline]
    list_per_page = 25

    @admin.action(description=_("Generate MembershipRemittance for current year"))
    def generate_remittance(self, request, families: QuerySet[Family]):
        academic_course: AcademicCourse = ActiveCourse.load()
        remittance = MembershipRemittanceCreator(families, academic_course).create()
        message = mark_safe(_("Membership remittance created") + " (<a href=\"" + remittance.get_admin_url() + "\">" + _("View details") + "</a>)")
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
        for family in families:
            if Membership.is_member_family(family):
                already_members += 1
            else:
                Membership.make_member_for_active_course(family)
                new_members += 1

        message = _('%(new_members)s families became members. %(already_members)s families already were members') % {'new_members': new_members, 'already_members': already_members}
        return self.message_user(request=request, message=message)         

    @admin.display(description=_('Children'))
    def children_count(self, family):
        return family.get_children_count()
    
    @admin.display(description=_('In school'))
    def children_in_school_count(self, family):
        return family.get_children_in_school_count()
    
    @admin.display(description=_('Is member'))
    def is_member(self, family):
        return _('Yes') if Membership.is_member_family(family) else _('No')
    
    actions = [generate_remittance, export_emails, make_members]


class BankAccountInline(admin.TabularInline):
    model = BankAccount
    fields = ['swift_bic', 'iban', 'owner']
    extra = 0


class ParentAdmin(admin.ModelAdmin):
    list_display = ['name_and_surnames', 'parent_families', 'phone_number', 'additional_phone_number', 'is_member']
    fields = ['name_and_surnames', 'phone_number', 'additional_phone_number', 'created', 'modified']
    readonly_fields = ['created', 'modified']
    ordering = ['name_and_surnames']
    search_fields = ['name_and_surnames', 'family__surnames', 'phone_number', 'additional_phone_number']
    inlines = [BankAccountInline]
    list_per_page = 25

    @admin.display(description=_('Is member'))
    def is_member(self, parent):
        return _('Yes') if Membership.objects.by_parent(parent).exists() else _('No')
    
    @admin.display(description=_('Family'))
    def parent_families(self, parent):
        return ', '.join(str(f) for f in parent.family_set.all())
    

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
        return child.get_level_name()
    
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
            authorization = Authorization.objects.get(bank_account=bank_account)
            return State.get_value_hunman_name(authorization.state)
        except Authorization.DoesNotExist:
            return _('No authorizacion')


class AuthorizationAdmin(admin.ModelAdmin):
    list_display = ['number', 'year', 'date', 'bank_account', 'document', 'state']
    ordering = ['-date']
    list_filter = ['year', 'state']
    search_fields = ['number', 'year', 'date', 'bank_account']
    list_per_page = 25

    @admin.action(description=_("Set as not sent"))
    def set_as_not_sent(self, request, queryset: QuerySet[Authorization]):
        queryset.update(state=State.NOT_SENT)

        message = _("%(num_authorizations)s authorizations set as NOT sent") % {'num_authorizations':  queryset.count()}
        self.message_user(request=request, message=message)

    @admin.action(description=_("Set as sent"))
    def set_as_sent(self, request, queryset: QuerySet[Authorization]):
        queryset.update(state=State.SENT)

        message = _("%(num_authorizations)s authorizations set as sent") % {'num_authorizations':  queryset.count()}
        self.message_user(request=request, message=message)
    
    @admin.action(description=_("Set as signed"))
    def set_as_signed(self, request, queryset: QuerySet[Authorization]):
        queryset.update(state=State.SIGNED)

        message = _("%(num_authorizations)s authorizations set as signed") % {'num_authorizations':  queryset.count()}
        self.message_user(request=request, message=message)
    
    actions = [set_as_not_sent, set_as_sent, set_as_signed]


class MembershipAdmin(admin.ModelAdmin):
    list_display = ['family', 'academic_course']
    ordering = ['-academic_course', 'family__surnames']
    list_filter = ['academic_course__initial_year']
    search_fields = ['family', 'academic_course']
    list_per_page = 25
