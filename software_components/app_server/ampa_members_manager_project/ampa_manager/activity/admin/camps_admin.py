from django.contrib import admin
from django.db.models import QuerySet
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, gettext_lazy

from ampa_manager.activity.admin.camps_edition_filters import CampsEditionHasRemittanceFilter

from ampa_manager.activity.admin.registration_filters import ChildLevelListFilter, RegistrationFilter
from ampa_manager.activity.models.camps.camps_edition import CampsEdition
from ampa_manager.activity.models.camps.camps_registration import CampsRegistration
from ampa_manager.charge.models.camps.camps_remittance import CampsRemittance
from ampa_manager.charge.use_cases.camps.camps_remittance_creator.camps_remittance_creator import \
    CampsRemittanceCreator
from ampa_manager.family.models.membership import Membership
from ampa_manager.read_only_inline import ReadOnlyTabularInline


class CampsRegistrationAdmin(admin.ModelAdmin):
    list_display = ['camps_edition', 'child', 'holder', 'is_member']
    ordering = ['camps_edition']
    list_filter = ['camps_edition__academic_course__initial_year', RegistrationFilter, ChildLevelListFilter]
    search_fields = ['child__name', 'child__family__surnames', 'holder__bank_account__iban',
                     'holder__parent__name_and_surnames']
    list_per_page = 25

    @admin.display(description=gettext_lazy('Is member'))
    def is_member(self, registration):
        return _('Yes') if Membership.is_member_child(registration.child) else _('No')


class CampsRegistrationInline(ReadOnlyTabularInline):
    model = CampsRegistration
    fields = ['camps_edition', 'child', 'is_member', 'holder']
    readonly_fields = fields
    ordering = ['camps_edition', 'child__name', 'child__family__surnames']

    @admin.display(description=gettext_lazy('Is member'), boolean=True)
    def is_member(self, registration):
        return Membership.is_member_child(registration.child)


class CampsEditionAdmin(admin.ModelAdmin):
    inlines = [CampsRegistrationInline]
    list_display = ['academic_course', 'levels', 'price_for_member', 'price_for_no_member',
                    'members_registrations_count', 'no_members_registrations_count',
                    'registrations_count', 'remittance']
    fieldsets = (
        (None, {'fields': ('academic_course', 'levels')}),
        (_('Prices'), {'fields': ('price_for_member', 'price_for_no_member'), }),
        (_('Registrations'), {
            'fields': ('members_registrations_count', 'no_members_registrations_count', 'registrations_count'),
        }),
        (_('Remittance'), {'fields': ('remittance',), }),
    )
    readonly_fields = ['remittance', 'members_registrations_count', 'no_members_registrations_count',
                       'registrations_count']
    ordering = ['-academic_course', '-id']
    list_filter = ['academic_course__initial_year', CampsEditionHasRemittanceFilter]
    list_per_page = 25

    @admin.display(description=gettext_lazy('No members'))
    def no_members_registrations_count(self, edition):
        return edition.no_members_registrations_count

    @admin.display(description=gettext_lazy('Members'))
    def members_registrations_count(self, edition):
        return edition.members_registrations_count

    @admin.display(description=gettext_lazy('Total'))
    def registrations_count(self, edition):
        return edition.registrations_count

    @admin.display(description=gettext_lazy('Remittance'))
    def remittance(self, edition):
        remittances = CampsRemittance.objects.filter(camps_editions=edition)
        if remittances.count() == 1:
            return str(remittances.first())
        elif remittances.count() == 0:
            return '-'
        else:
            return _('Multiple remittances')

    @admin.action(description=_("Create camps remittance"))
    def create_camps_remittance(self, request, camps_editions: QuerySet[CampsEdition]):
        camps_remittance = CampsRemittanceCreator(camps_editions).create()
        url = camps_remittance.get_admin_url()
        message = mark_safe(
            _("Activity remittance created") + " (<a href=\"" + url + "\">" + _("View details") + "</a>)")
        return self.message_user(request=request, message=message)

    actions = [create_camps_remittance]
