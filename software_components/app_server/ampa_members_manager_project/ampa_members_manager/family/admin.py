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


class FamilyAdmin(admin.ModelAdmin):
    list_display = ['first_surname', 'second_surname', 'email', 'secondary_email', 'default_bank_account']
    search_fields = ['first_surname', 'second_surname', 'email', 'secondary_email']
    form = FamilyAdminForm
    filter_horizontal = ['parents']
    inlines = [ChildInline]

    @admin.action(description=_("Generate MembershipRemittance for current year"))
    def generate_remittance(self, request, families: QuerySet[Family]):
        academic_course: AcademicCourse = ActiveCourse.load()
        MembershipRemittanceCreator(families, academic_course).create()
        return self.message_user(request=request, message=_("Membership Remittance created"))

    actions = [generate_remittance]


class ParentAdmin(admin.ModelAdmin):
    list_display = ['name', 'first_surname', 'second_surname', 'phone_number']
    search_fields = ['name', 'first_surname', 'second_surname', 'phone_number']


class ChildAdmin(admin.ModelAdmin):
    list_display = ['name', 'year_of_birth', 'repetition', 'family']
    list_filter = ['year_of_birth', 'repetition']
    search_fields = ['name', 'year_of_birth', 'repetition', 'family']


class AuthorizationInline(admin.TabularInline):
    model = Authorization
    extra = 0


class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['swift_bic', 'iban', 'owner']
    list_filter = ['swift_bic']
    search_fields = ['swift_bic', 'iban', 'owner']
    inlines = [AuthorizationInline]


class AuthorizationAdmin(admin.ModelAdmin):
    list_display = ['number', 'year', 'bank_account', 'document']
    list_filter = ['year']
    search_fields = ['number', 'year', 'bank_account']


class MembershipAdmin(admin.ModelAdmin):
    list_display = ['family', 'academic_course']
    list_filter = ['academic_course']
    search_fields = ['family', 'academic_course']
