from django import forms
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.charge.admin import MembershipReceiptInline
from ampa_manager.charge.models.activity_receipt import ActivityReceipt
from ampa_manager.charge.use_cases.membership.create_membership_remittance_with_families.membership_remittance_creator import \
    MembershipRemittanceCreator
from ampa_manager.family.admin.filters.family_filters import FamilyIsMemberFilter, FamilyChildrenCountFilter, \
    FamilyDefaultAccountFilter, FamilyParentCountFilter
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.membership import Membership
from ampa_manager.non_related_inlines import NonrelatedTabularInline
from ampa_manager.read_only_inline import ReadOnlyTabularInline


class FamilyAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['default_holder'].queryset = Holder.objects.of_family(self.instance)
        else:
            self.fields['default_holder'].queryset = Holder.objects.none()


class FamilyActivityReceiptInline(NonrelatedTabularInline):

    def save_new_instance(self, parent, instance):
        """ must be implemented but not used"""
        pass

    model = ActivityReceipt
    fields = ['amount', 'state']

    def get_form_queryset(self, family):
        return ActivityReceipt.objects.of_family(family)


class MembershipInline(ReadOnlyTabularInline):
    model = Membership
    extra = 0


class ChildInline(admin.TabularInline):
    model = Child
    extra = 0


class FamilyAdmin(admin.ModelAdmin):
    list_display = ['surnames', 'default_holder', 'parent_count',
                    'children_in_school_count', 'is_member', 'created_formatted']
    fields = ['surnames', 'parents', 'default_holder', 'decline_membership', 'is_defaulter',
              'created', 'modified']
    readonly_fields = ['created', 'modified']
    ordering = ['surnames']
    list_filter = [FamilyIsMemberFilter, FamilyChildrenCountFilter, FamilyDefaultAccountFilter, 'created', 'modified',
                   'is_defaulter', 'decline_membership', FamilyParentCountFilter]
    search_fields = ['surnames', 'parents__name_and_surnames', 'id']
    form = FamilyAdminForm
    filter_horizontal = ['parents']
    inlines = [ChildInline, MembershipInline, MembershipReceiptInline, FamilyActivityReceiptInline]
    list_per_page = 25

    @admin.action(description=gettext_lazy("Generate MembershipRemittance for current year"))
    def generate_remittance(self, request, families: QuerySet[Family]):
        academic_course: AcademicCourse = ActiveCourse.load()
        remittance = MembershipRemittanceCreator(families, academic_course).create()
        if remittance:
            message = mark_safe(
                gettext_lazy(
                    "Membership remittance created") + " (<a href=\"" + remittance.get_admin_url() + "\">" + gettext_lazy(
                    "View details") + "</a>)")
        else:
            message = gettext_lazy("No families to include in Membership Remittance")
        return self.message_user(request=request, message=message)

    @admin.action(description=gettext_lazy("Export emails to CSV"))
    def export_emails(self, _, families: QuerySet[Family]):
        emails = []
        for family in families:
            for parent in family.parents.all():
                if parent.email and parent.email not in emails:
                    emails.append(parent.email)

        headers = {'Content-Disposition': f'attachment; filename="emails.csv"'}
        return HttpResponse(content_type='text/csv', headers=headers, content=",".join(emails))

    @admin.action(description=gettext_lazy("Make families member"))
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

        message = gettext_lazy(
            '%(new_members)s families became members. %(already_members)s families already were members. %(declined)s families declined to be members anymore') % {
                      'new_members': new_members, 'already_members': already_members, 'declined': declined}
        return self.message_user(request=request, message=message)

    @admin.action(description=gettext_lazy("Decline Membership"))
    def decline_membership(self, request, families: QuerySet[Family]):
        for family in families.iterator():
            family.to_decline_membership()
        message = gettext_lazy("Decline Membership established")
        return self.message_user(request=request, message=message)

    @admin.display(description=gettext_lazy('Parents'))
    def parent_count(self, family):
        return family.get_parent_count()

    @admin.display(description=gettext_lazy('Children'))
    def children_count(self, family):
        return family.get_children_count()

    @admin.display(description=gettext_lazy('In school'))
    def children_in_school_count(self, family):
        return f'{family.get_children_in_school_count()}/{family.get_children_count()}'

    @admin.display(description=gettext_lazy('Is member'))
    def is_member(self, family):
        return gettext_lazy('Yes') if Membership.is_member_family(family) else gettext_lazy('No')

    @admin.display(description=gettext_lazy('Created'))
    def created_formatted(self, family):
        return family.created.strftime('%d/%m/%y, %H:%M')

    created_formatted.admin_order_field = 'created'

    actions = [generate_remittance, export_emails, make_members]
