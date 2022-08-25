from django import forms
from django.contrib import admin
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.academic_course.models.academic_course import AcademicCourse
from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.charge.use_cases.create_membership_remittance_with_families.membership_remittance_creator import \
    MembershipRemittanceCreator
from ampa_members_manager.family.models.authorization import Authorization
from ampa_members_manager.family.models.bank_account import BankAccount
from ampa_members_manager.family.models.child import Child
from ampa_members_manager.family.models.family import Family
from ampa_members_manager.family.models.membership import Membership
from ampa_members_manager.family.filters import CourseListFilter
from ampa_members_manager.family.models.state import State
from ampa_members_manager.academic_course.models.course_name import CourseName


class FamilyAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['default_bank_account'].queryset = BankAccount.objects.filter(owner__family=self.instance)
        else:
            self.fields['default_bank_account'].queryset = BankAccount.objects.none()


class ChildInline(admin.TabularInline):
    model = Child
    extra = 0


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0


class FamilyAdmin(admin.ModelAdmin):
    list_display = ['surnames', 'email', 'secondary_email', 'default_bank_account', 'child_count', 'is_member']
    search_fields = ['surnames', 'email', 'secondary_email']
    form = FamilyAdminForm
    filter_horizontal = ['parents']
    inlines = [ChildInline, MembershipInline]

    @admin.action(description=_("Generate MembershipRemittance for current year"))
    def generate_remittance(self, request, families: QuerySet[Family]):
        academic_course: AcademicCourse = ActiveCourse.load()
        MembershipRemittanceCreator(families, academic_course).create()
        return self.message_user(request=request, message=_("Membership Remittance created"))
    
    @admin.display(description=_('Children'))
    def child_count(self, family):
        return family.child_set.count()
    
    @admin.display(description=_('Is member'))
    def is_member(self, family):
        return _('Yes') if family.membership_set.filter(academic_course=ActiveCourse.load()).exists() else _('No')
    
    actions = [generate_remittance]


class BankAccountInline(admin.TabularInline):
    model = BankAccount
    fields = ['swift_bic', 'iban', 'owner']
    extra = 0


class ParentAdmin(admin.ModelAdmin):
    list_display = ['name_and_surnames', 'phone_number']
    search_fields = ['name_and_surnames', 'phone_number']
    inlines = [BankAccountInline]


class ChildAdmin(admin.ModelAdmin):
    list_display = ['name', 'family', 'parents', 'year_of_birth', 'repetition', 'child_course', 'is_member']
    list_filter = ['year_of_birth', 'repetition', CourseListFilter]
    search_fields = ['name', 'year_of_birth', 'repetition', 'family']

    @admin.display(description=_('Is member'))
    def is_member(self, child):
        return _('Yes') if child.family.membership_set.filter(academic_course=ActiveCourse.load()).exists() else _('No')
    
    @admin.display(description=_('Course'))
    def child_course(self, child):
        return child.get_course_name()
    
    @admin.display(description=_('Parents'))
    def parents(self, child):
        return ', '.join(p.name_and_surnames for p in child.family.parents.all())


class AuthorizationInline(admin.TabularInline):
    model = Authorization
    extra = 0


class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['swift_bic', 'iban', 'owner']
    list_filter = ['swift_bic']
    search_fields = ['swift_bic', 'iban', 'owner']
    inlines = [AuthorizationInline]


class AuthorizationAdmin(admin.ModelAdmin):
    list_display = ['number', 'year', 'date', 'bank_account', 'document', 'state']
    list_filter = ['year', 'state']
    search_fields = ['number', 'year', 'date', 'bank_account']

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
    list_filter = ['academic_course__initial_year']
    search_fields = ['family', 'academic_course']
