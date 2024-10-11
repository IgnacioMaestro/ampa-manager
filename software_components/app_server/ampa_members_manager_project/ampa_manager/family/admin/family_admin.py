from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy
from django.utils.translation import gettext_lazy as _
from openpyxl import Workbook

from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.academic_course.models.level import Level
from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.activity.models.camps.camps_registration import CampsRegistration
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.charge.models.after_school_charge.after_school_receipt import AfterSchoolReceipt
from ampa_manager.charge.models.camps.camps_receipt import CampsReceipt
from ampa_manager.charge.models.custody.custody_receipt import CustodyReceipt
from ampa_manager.charge.models.membership_receipt import MembershipReceipt
from ampa_manager.family.admin.filters.family_filters import FamilyIsMemberFilter, FamilyChildrenInSchoolFilter, \
    MembershipHolder, CustodyHolder, FamilyParentCountFilter, CampsHolder, AnyHolder, AfterSchoolHolder, FamilyEmail
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.membership import Membership
from ampa_manager.family.use_cases.auto_complete_holders import AutoCompleteHolders
from ampa_manager.read_only_inline import ReadOnlyTabularInline
from ampa_manager.utils.utils import Utils


class FamilyAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['membership_holder'].queryset = Holder.objects.of_family(self.instance)
            self.fields['custody_holder'].queryset = Holder.objects.of_family(self.instance)
            self.fields['after_school_holder'].queryset = Holder.objects.of_family(self.instance)
            self.fields['camps_holder'].queryset = Holder.objects.of_family(self.instance)
        else:
            self.fields['membership_holder'].queryset = Holder.objects.none()
            self.fields['custody_holder'].queryset = Holder.objects.none()
            self.fields['after_school_holder'].queryset = Holder.objects.none()
            self.fields['camps_holder'].queryset = Holder.objects.none()


class MembershipInline(ReadOnlyTabularInline):
    model = Membership
    extra = 0


class ChildInline(ReadOnlyTabularInline):
    model = Child
    fields = ['name', 'year_of_birth', 'repetition', 'child_course', 'after_school_registrations',
              'custody_registrations', 'camps_registrations', 'link']
    readonly_fields = ['child_course', 'after_school_registrations', 'custody_registrations', 'camps_registrations',
                       'link']
    extra = 0

    @admin.display(description=_('Id'))
    def link(self, child):
        return child.get_html_link(True)

    @admin.display(description=_('Course'))
    def child_course(self, child):
        return Level.get_level_name(child.level)

    @admin.display(description=_('After-schools') + ' (' + _('This year') + ' / ' + _('Previously') + ')')
    def after_school_registrations(self, child):
        active_course = AfterSchoolRegistration.objects.of_child(child).of_active_course().count()
        previous_courses = AfterSchoolRegistration.objects.of_child(child).of_previous_courses().count()
        return f'{active_course} / {previous_courses}'

    @admin.display(description=_('Custody') + ' (' + _('This year') + ' / ' + _('Previously') + ')')
    def custody_registrations(self, child):
        active_course = CustodyRegistration.objects.of_child(child).of_active_course().count()
        previous_courses = CustodyRegistration.objects.of_child(child).of_previous_courses().count()
        return f'{active_course} / {previous_courses}'

    @admin.display(description=_('Camps') + ' (' + _('This year') + ' / ' + _('Previously') + ')')
    def camps_registrations(self, child):
        active_course = CampsRegistration.objects.of_child(child).of_active_course().count()
        previous_courses = CampsRegistration.objects.of_child(child).of_previous_courses().count()
        return f'{active_course} / {previous_courses}'


class FamilyInline(ReadOnlyTabularInline):
    model = Family.parents.through


class FamilyAdmin(admin.ModelAdmin):
    list_display = ['surnames', 'email', 'secondary_email', 'parents_names', 'children_names',  'children_in_school_count', 'is_member',
                    'has_membership_holder', 'created_formatted', 'id']
    fieldsets = (
        (_('General'), {
            'fields': ['surnames', 'email', 'secondary_email', 'parents', 'decline_membership', 'is_defaulter', 'created', 'modified']
        }),
        (_('Payment details'), {
            'fields': ['membership_holder', 'custody_holder', 'camps_holder', 'after_school_holder'],
        }),
        (_('Registrations'), {
            'fields': ['camps_registrations', 'custody_registrations', 'after_school_registrations'],
        }),
        (_('Receipts'), {
            'fields': ['membership_receipts', 'camps_receipts', 'custody_receipts', 'after_school_receipts'],
        }),
    )

    readonly_fields = ['created', 'modified', 'membership_receipts', 'camps_receipts', 'custody_receipts',
                       'after_school_receipts', 'camps_registrations', 'custody_registrations',
                       'after_school_registrations']
    ordering = ['surnames']
    list_filter = [FamilyIsMemberFilter, FamilyChildrenInSchoolFilter, 'created', 'modified', 'is_defaulter',
                   'decline_membership', FamilyParentCountFilter, MembershipHolder, CustodyHolder, CampsHolder,
                   AfterSchoolHolder, AnyHolder, FamilyEmail]
    search_fields = ['surnames', 'normalized_surnames', 'email', 'secondary_email', 'parents__name_and_surnames', 'id',
                     'child__name', 'parents__email', 'membership_holder__bank_account__iban',
                     'custody_holder__bank_account__iban', 'camps_holder__bank_account__iban',
                     'after_school_holder__bank_account__iban']
    form = FamilyAdminForm
    filter_horizontal = ['parents']
    inlines = [ChildInline, MembershipInline]
    list_per_page = 25

    @admin.action(description=gettext_lazy("Complete missing holders"))
    def complete_holders(self, request, families: QuerySet[Family]):
        custody_holders_before = families.exclude(camps_holder=None).count()
        after_school_holders_before = families.exclude(camps_holder=None).count()
        camps_holders_before = families.exclude(camps_holder=None).count()
        membership_holders_before = families.exclude(membership_holder=None).count()

        for family in families:
            AutoCompleteHolders.complete_holders(family)

        custody_holders_after = families.exclude(camps_holder=None).count()
        after_school_holders_after = families.exclude(camps_holder=None).count()
        camps_holders_after = families.exclude(camps_holder=None).count()
        membership_holders_after = families.exclude(membership_holder=None).count()

        message = gettext_lazy(
            'Membership holders: %(membership_holders_before)s -> %(membership_holders_after)s <br/>'
            'Custody holders: %(custody_holders_before)s -> %(custody_holders_after)s <br/>'
            'After-schools holders: %(after_school_holders_before)s -> %(after_school_holders_after)s <br/>'
            'Camps holders: %(camps_holders_before)s -> %(camps_holders_after)s') % {
                      'custody_holders_before': custody_holders_before,
                      'after_school_holders_before': after_school_holders_before,
                      'camps_holders_before': camps_holders_before,
                      'membership_holders_before': membership_holders_before,
                      'custody_holders_after': custody_holders_after,
                      'after_school_holders_after': after_school_holders_after,
                      'camps_holders_after': camps_holders_after,
                      'membership_holders_after': membership_holders_after}
        self.message_user(request=request, message=mark_safe(message))

    @admin.action(description=gettext_lazy("Export family and parents emails to CSV"))
    def export_all_emails(self, request, families: QuerySet[Family]):
        emails = Family.get_families_parents_emails(families)
        emails_csv = ",".join(emails)
        headers = {'Content-Disposition': f'attachment; filename="correos.csv"'}
        return HttpResponse(content_type='text/csv', headers=headers, content=emails_csv)

    @admin.action(description=gettext_lazy("Export only family emails to CSV"))
    def export_family_emails(self, request, families: QuerySet[Family]):
        emails = Family.get_families_parents_emails(families, parents_emails=False, family_emails=True)
        emails_csv = ",".join(emails)
        headers = {'Content-Disposition': f'attachment; filename="correos.csv"'}
        return HttpResponse(content_type='text/csv', headers=headers, content=emails_csv)

    @admin.action(description=gettext_lazy("Send email to the parents of selected families"))
    def send_email_to_parents(self, request, families: QuerySet[Family]):
        emails = Family.get_families_parents_emails(families)
        emails_csv = ",".join(emails)
        email = settings.FROM_EMAIL
        link_href = f"mailto:{email}?bcc={emails_csv}"
        link_text = gettext_lazy("Click here to send an email to the parents")
        link_html = f'<a target="_new" href="{link_href}">{link_text}</a>'
        return messages.success(request, mark_safe(link_html))

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

    @admin.action(description=gettext_lazy("Remove from members"))
    def undo_members(self, request, families: QuerySet[Family]):
        removed_members = 0
        non_members = 0
        active_course = ActiveCourse.load()

        for family in families:

            try:
                membership = Membership.objects.get(family=family, academic_course=active_course)
                membership.delete()
                removed_members += 1
            except Membership.DoesNotExist:
                non_members += 1

        message = gettext_lazy(
            '%(removed_members)s families removed from members. '
            '%(non_members)s of the selected families were not members') % {
                      'removed_members': removed_members, 'non_members': non_members}
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
    def has_membership_holder(self, family):
        return gettext_lazy('Yes') if family.membership_holder is not None else gettext_lazy('No')

    @admin.display(description=gettext_lazy('Created'))
    def created_formatted(self, family):
        return family.created.strftime('%d/%m/%y, %H:%M')

    @admin.display(description=gettext_lazy('Membership receipts'))
    def membership_receipts(self, family):
        receipts_count = MembershipReceipt.objects.of_family(family).count()
        if receipts_count == 1:
            link_text = gettext_lazy('%(num_receipts)s receipt') % {'num_receipts': receipts_count}
        else:
            link_text = gettext_lazy('%(num_receipts)s receipts') % {'num_receipts': receipts_count}
        filters = f'family={family.id}'
        return Utils.get_model_link(model_name=MembershipReceipt.__name__.lower(), link_text=link_text, filters=filters)

    @admin.display(description=gettext_lazy('Camps receipts'))
    def camps_receipts(self, family):
        receipts_count = CampsReceipt.objects.of_family(family).count()
        if receipts_count == 1:
            link_text = gettext_lazy('%(num_receipts)s receipt') % {'num_receipts': receipts_count}
        else:
            link_text = gettext_lazy('%(num_receipts)s receipts') % {'num_receipts': receipts_count}
        filters = f'family={family.id}'
        return Utils.get_model_link(model_name=CampsReceipt.__name__.lower(), link_text=link_text, filters=filters)

    @admin.display(description=gettext_lazy('Custody receipts'))
    def custody_receipts(self, family):
        receipts_count = CustodyReceipt.objects.of_family(family).count()
        if receipts_count == 1:
            link_text = gettext_lazy('%(num_receipts)s receipt') % {'num_receipts': receipts_count}
        else:
            link_text = gettext_lazy('%(num_receipts)s receipts') % {'num_receipts': receipts_count}
        filters = f'family={family.id}'
        return Utils.get_model_link(model_name=CustodyReceipt.__name__.lower(), link_text=link_text, filters=filters)

    @admin.display(description=gettext_lazy('Custody registrations'))
    def custody_registrations(self, family):
        return self.get_registrations_link(family, CustodyRegistration)

    @admin.display(description=gettext_lazy('Camps registrations'))
    def camps_registrations(self, family):
        return self.get_registrations_link(family, CampsRegistration)

    @admin.display(description=gettext_lazy('After-school registrations'))
    def after_school_registrations(self, family):
        return self.get_registrations_link(family, AfterSchoolRegistration)

    def get_registrations_link(self, family, registration_model):
        registrations_count = registration_model.objects.of_family(family).count()
        if registrations_count == 1:
            link_text = (gettext_lazy('%(registrations)s registration') % {'registrations': registrations_count})
        else:
            link_text = (gettext_lazy('%(registrations)s registrations') % {'registrations': registrations_count})

        filters = f'family={family.id}'
        return Utils.get_model_link(model_name=registration_model.__name__.lower(), link_text=link_text,
                                    filters=filters)

    @admin.display(description=gettext_lazy('After-school receipts'))
    def after_school_receipts(self, family):
        receipts_count = AfterSchoolReceipt.objects.of_family(family).count()
        if receipts_count == 1:
            link_text = gettext_lazy('%(num_receipts)s receipt') % {'num_receipts': receipts_count}
        else:
            link_text = gettext_lazy('%(num_receipts)s receipts') % {'num_receipts': receipts_count}
        filters = f'family={family.id}'
        return Utils.get_model_link(model_name=AfterSchoolReceipt.__name__.lower(), link_text=link_text, filters=filters)

    created_formatted.admin_order_field = 'created'

    actions = [export_all_emails, export_family_emails, make_members, undo_members, export_families_xls, complete_holders]
