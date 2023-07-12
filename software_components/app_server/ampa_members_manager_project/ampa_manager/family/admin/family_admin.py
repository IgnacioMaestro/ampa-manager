from django import forms
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy
from openpyxl import Workbook

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.academic_course.models.level import Level
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.activity.models.camps.camps_registration import CampsRegistration
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.charge.use_cases.membership.create_membership_remittance_with_families.membership_remittance_creator import \
    MembershipRemittanceCreator
from ampa_manager.family.admin.filters.family_filters import FamilyIsMemberFilter, FamilyChildrenCountFilter, \
    DefaultHolder, CustodyHolder, FamilyParentCountFilter
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.membership import Membership
from ampa_manager.read_only_inline import ReadOnlyTabularInline


class FamilyAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['default_holder'].queryset = Holder.objects.of_family(self.instance)
            self.fields['custody_holder'].queryset = Holder.objects.of_family(self.instance)
        else:
            self.fields['default_holder'].queryset = Holder.objects.none()
            self.fields['custody_holder'].queryset = Holder.objects.none()


class MembershipInline(ReadOnlyTabularInline):
    model = Membership
    extra = 0


class ChildInline(ReadOnlyTabularInline):
    model = Child
    fields = ['name', 'year_of_birth', 'repetition', 'child_course', 'after_school_registration_count',
              'custody_registration_count', 'camps_registration_count', 'link']
    readonly_fields = ['child_course', 'after_school_registration_count', 'custody_registration_count',
                       'camps_registration_count', 'link']
    extra = 0

    @admin.display(description=_('Id'))
    def link(self, child):
        return child.get_html_link(True)

    @admin.display(description=_('Course'))
    def child_course(self, child):
        return Level.get_level_name(child.level)

    @admin.display(description=_('After-schools'))
    def after_school_registration_count(self, child):
        return AfterSchoolRegistration.objects.of_child(child).of_academic_course(ActiveCourse.load()).count()

    @admin.display(description=_('Custody'))
    def custody_registration_count(self, child):
        return CustodyRegistration.objects.of_child(child).of_academic_course(ActiveCourse.load()).count()

    @admin.display(description=_('Camps'))
    def camps_registration_count(self, child):
        return CampsRegistration.objects.of_child(child).of_academic_course(ActiveCourse.load()).count()


class FamilyAdmin(admin.ModelAdmin):
    list_display = ['surnames', 'parents_names', 'children_names',
                    'children_in_school_count', 'is_member', 'has_default_holder', 'created_formatted']
    fields = ['surnames', 'parents', 'default_holder', 'custody_holder', 'decline_membership', 'is_defaulter',
              'created', 'modified']
    readonly_fields = ['created', 'modified']
    ordering = ['surnames']
    list_filter = [FamilyIsMemberFilter, FamilyChildrenCountFilter, 'created', 'modified', 'is_defaulter',
                   'decline_membership', FamilyParentCountFilter, DefaultHolder, CustodyHolder]
    search_fields = ['surnames', 'parents__name_and_surnames', 'id', 'child__name']
    form = FamilyAdminForm
    filter_horizontal = ['parents']
    inlines = [ChildInline, MembershipInline]
    list_per_page = 50

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

    @admin.action(description=gettext_lazy("Complete empty custody holders with last registration"))
    def complete_custody_holder_with_last_registration(self, request, families: QuerySet[Family]):
        updated = 0
        for family in families:
            if not family.custody_holder:
                last_registration = CustodyRegistration.objects.filter(child__family=family).order_by('-id').last()
                if last_registration and last_registration.holder:
                    family.custody_holder = last_registration.holder
                    family.save()
                    updated += 1

        message = gettext_lazy('%(update_families)s families updated') % {'update_families': updated}
        return self.message_user(request=request, message=message)

    @admin.action(description=gettext_lazy("Complete empty custody holders with default_holder"))
    def complete_custody_holder_with_default_holder(self, request, families: QuerySet[Family]):
        updated = 0
        for family in families:
            if not family.custody_holder and family.default_holder:
                family.custody_holder = family.default_holder
                family.save()
                updated += 1

        message = gettext_lazy('%(update_families)s families updated') % {'update_families': updated}
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

    @admin.action(description=gettext_lazy("Export families to XLS"))
    def export_families_xls(self, _, families: QuerySet[Family]):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',)
        response['Content-Disposition'] = 'attachment; filename=familias.xlsx'
        wb = Workbook()
        ws = wb.active

        active_course = str(ActiveCourse.load())

        column_titles = ['Apellidos familia', f'Socios curso {active_course}', 'Padre 1', 'Padre 2', 'Hijo 1', 'Hijo 2',
                         'Hijo 3', 'Hijo 4', 'Hijo 5']
        ws.append(column_titles)

        for family in families:
            ws.append(FamilyAdmin.get_family_xls_fields(family))

        wb.save(response)

        return response

    @classmethod
    def get_family_xls_fields(cls, family):
        parents = [p.name_and_surnames.encode('utf-8') for p in family.parents.all()]
        for i in range(len(parents), 2):
            parents.append('')

        children = [c.name.encode('utf-8') for c in family.child_set.all()]
        for i in range(len(parents), 5):
            children.append('')

        is_member = Membership.is_member_family(family)
        is_member_text = 'Sí' if is_member else 'No'

        fields = [family.surnames, is_member_text]
        fields.extend(parents)
        fields.extend(children)
        return fields

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
    def parents_names(self, family):
        return family.parents_names

    @admin.display(description=gettext_lazy('Children'))
    def children_names(self, family):
        return family.children_names

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

    @admin.display(description=gettext_lazy('Default holder'))
    def has_default_holder(self, family):
        return gettext_lazy('Yes') if family.default_holder is not None else gettext_lazy('No')

    @admin.display(description=gettext_lazy('Created'))
    def created_formatted(self, family):
        return family.created.strftime('%d/%m/%y, %H:%M')

    created_formatted.admin_order_field = 'created'

    actions = [generate_remittance, export_emails, make_members, export_families_xls,
               complete_custody_holder_with_last_registration, complete_custody_holder_with_default_holder]
