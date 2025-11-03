import json
from datetime import datetime
from typing import Optional

from django import forms
from django.contrib import admin, messages
from django.db.models import QuerySet
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, gettext_lazy

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.activity.admin.registration_filters import (FamilyRegistrationFilter,
                                                              AfterSchoolRegistrationRemittanceFilter)
from ampa_manager.activity.models.after_school.after_school import AfterSchool
from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.charge.models.after_school_charge.after_school_receipt import AfterSchoolReceipt
from ampa_manager.charge.models.after_school_charge.after_school_remittance import AfterSchoolRemittance
from ampa_manager.charge.use_cases.after_school.after_school_remittance_creator.after_school_remittance_creator import \
    AfterSchoolRemittanceCreator
from ampa_manager.charge.use_cases.remittance_creator_error import RemittanceCreatorError
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.membership import Membership
from ampa_manager.family.use_cases.family_emails_exporter import FamilyEmailExporter
from ampa_manager.read_only_inline import ReadOnlyTabularInline
from ampa_manager.utils.csv_http_response import CsvHttpResponse
from ampa_manager.utils.db_utils import distinct_count
from ampa_manager.utils.utils import Utils


class AfterSchoolRegistrationAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'child'):
            self.fields['holder'].queryset = Holder.objects.of_family(self.instance.child.family)
        else:
            self.fields['holder'].queryset = Holder.objects.none()


class AfterSchoolRegistrationAdmin(admin.ModelAdmin):
    list_display = ['course', 'after_school', 'timetable', 'family_surnames', 'child_name', 'holder', 'is_member',
                    'price', 'receipts_count']
    ordering = ['-after_school_edition__academic_course__initial_year', 'after_school_edition__after_school__name']
    list_filter = ['after_school_edition__academic_course__initial_year', AfterSchoolRegistrationRemittanceFilter,
                   'after_school_edition__period',
                   'after_school_edition__timetable',
                   'after_school_edition__levels',
                   'after_school_edition__after_school__name', FamilyRegistrationFilter]
    search_fields = ['id', 'child__name', 'child__family__surnames', 'after_school_edition__after_school__name',
                     'holder__bank_account__iban', 'holder__parent__name_and_surnames',
                     'child__family__email', 'child__family__secondary_email']
    autocomplete_fields = ['after_school_edition', 'holder', 'child']
    list_per_page = 25

    # form = AfterSchoolRegistrationAdminForm

    @admin.display(description=gettext_lazy('Receipts'))
    def receipts_count(self, registration):
        return registration.afterschoolreceipt_set.count()

    @admin.display(description=gettext_lazy('Course'))
    def course(self, registration):
        return str(registration.after_school_edition.academic_course)

    @admin.display(description=gettext_lazy('Activity'))
    def after_school(self, registration):
        return registration.after_school_edition.after_school

    @admin.display(description=gettext_lazy('Timetable'))
    def timetable(self, registration):
        return registration.after_school_edition.timetable

    @admin.display(description=gettext_lazy('Child'))
    def child_name(self, registration):
        return registration.child.str_short()

    @admin.display(description=gettext_lazy('Family'))
    def family_surnames(self, registration):
        return registration.child.family.surnames

    @admin.display(description=gettext_lazy('Is member'))
    def is_member(self, registration):
        return _('Yes') if Membership.is_member_child(registration.child) else _('No')

    @admin.display(description=gettext_lazy('Price'))
    def price(self, registration):
        return registration.calculate_price()

    @admin.action(description=gettext_lazy("Download IDs of selected registrations as CSV"))
    def download_ids_as_csv(self, request, registrations: QuerySet[AfterSchoolRegistration]):
        ids = []
        for registration in registrations.all():
            ids.append(str(registration.id))
        file_name = f"{len(ids)}_{_('registrations')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        file_content = ",".join(ids)
        return CsvHttpResponse(file_name, file_content)

    @admin.action(description=gettext_lazy("Download family emails"))
    def export_emails(self, request, registrations: QuerySet[AfterSchoolRegistration]):
        families = []
        for registration in registrations.all():
            families.append(registration.child.family)

        file_name = 'correos.csv'
        file_content = FamilyEmailExporter(families).export_to_csv()
        return CsvHttpResponse(file_name, file_content)

    actions = [export_emails, download_ids_as_csv]

class AfterSchoolRegistrationInline(ReadOnlyTabularInline):
    model = AfterSchoolRegistration
    list_display = ['after_school_edition', 'child', 'holder', 'link']
    readonly_fields = list_display
    ordering = ['after_school_edition__after_school__name', 'after_school_edition']

    @admin.display(description=_('Id'))
    def link(self, registration):
        return registration.get_html_link(True)


class AfterSchoolEditionAdmin(admin.ModelAdmin):
    inlines = [AfterSchoolRegistrationInline]
    list_display = ['academic_course', 'after_school', 'code', 'period', 'timetable', 'price_for_member',
                    'price_for_no_member', 'after_schools_count', 'receipts_link']
    autocomplete_fields = ['after_school']
    fieldsets = (
        (None, {
            'fields': ('academic_course', 'after_school', 'code')
        }),
        (_('Timetable'), {
            'fields': ('period', 'timetable', 'levels'),
        }),
        (_('Price'), {
            'fields': ('price_for_member', 'price_for_no_member'),
        }),
    )
    ordering = ['-academic_course', 'after_school']
    list_filter = ['academic_course__initial_year', 'after_school__name']
    search_fields = ['after_school__name', 'timetable', 'code', 'id']
    list_per_page = 25

    @admin.display(description=gettext_lazy('Receipts'))
    def receipts_link(self, edition):
        receipts_count = AfterSchoolReceipt.objects.of_edition(edition).count()
        if receipts_count == 1:
            link_text = gettext_lazy('%(num_receipts)s receipt') % {'num_receipts': receipts_count}
        else:
            link_text = gettext_lazy('%(num_receipts)s receipts') % {'num_receipts': receipts_count}
        filters = f'edition={edition.id}'
        return Utils.get_model_link(model_name=AfterSchoolReceipt.__name__.lower(), link_text=link_text,
                                    filters=filters)

    @admin.action(description=_("Create after school remittance"))
    def create_after_school_remittance(self, request, after_school_editions: QuerySet[AfterSchoolEdition]):
        after_school_remittance: Optional[AfterSchoolRemittance]
        error: Optional[RemittanceCreatorError]
        after_school_remittance, error = AfterSchoolRemittanceCreator(after_school_editions).create_full()
        if error == RemittanceCreatorError.BIC_ERROR:
            message = Utils.create_bic_error_message()
            return self.message_user(request=request, message=message, level=messages.ERROR)
        url = after_school_remittance.get_admin_url()
        message = mark_safe(
            _("Activity remittance created") + " (<a href=\"" + url + "\">" + _("View details") + "</a>)")
        return self.message_user(request=request, message=message)

    @admin.action(description=_("Create after school remittance with half"))
    def create_after_school_remittance_half(self, request, after_school_editions: QuerySet[AfterSchoolEdition]):
        after_school_remittance: Optional[AfterSchoolRemittance]
        error: Optional[RemittanceCreatorError]
        after_school_remittance, error = AfterSchoolRemittanceCreator(after_school_editions).create_half()
        if error == RemittanceCreatorError.BIC_ERROR:
            message = Utils.create_bic_error_message()
            return self.message_user(request=request, message=message, level=messages.ERROR)
        url = after_school_remittance.get_admin_url()
        message = mark_safe(
            _("Activity remittance created") + " (<a href=\"" + url + "\">" + _("View details") + "</a>)")
        return self.message_user(request=request, message=message)

    @admin.action(description=_("Create after school remittance with left"))
    def create_after_school_remittance_left(self, request, after_school_editions: QuerySet[AfterSchoolEdition]):
        after_school_remittance: Optional[AfterSchoolRemittance]
        error: Optional[RemittanceCreatorError]
        after_school_remittance, error = AfterSchoolRemittanceCreator(after_school_editions).create_left()
        if error == RemittanceCreatorError.BIC_ERROR:
            message = Utils.create_bic_error_message()
            return self.message_user(request=request, message=message, level=messages.ERROR)
        url = after_school_remittance.get_admin_url()
        message = mark_safe(
            _("Activity remittance created") + " (<a href=\"" + url + "\">" + _("View details") + "</a>)")
        return self.message_user(request=request, message=message)

    @admin.action(description=_("Create after school remittance with enrolment"))
    def create_after_school_remittance_with_enrolment(
            self, request, after_school_editions: QuerySet[AfterSchoolEdition]):
        after_school_remittance: Optional[AfterSchoolRemittance]
        error: Optional[RemittanceCreatorError]
        after_school_remittance, error = AfterSchoolRemittanceCreator(after_school_editions).create_specific(25.0)
        if error == RemittanceCreatorError.BIC_ERROR:
            message = Utils.create_bic_error_message()
            return self.message_user(request=request, message=message, level=messages.ERROR)
        url = after_school_remittance.get_admin_url()
        message = mark_safe(
            _("Activity remittance created") + " (<a href=\"" + url + "\">" + _("View details") + "</a>)")
        return self.message_user(request=request, message=message)

    @admin.display(description=_('Registrations'))
    def after_schools_count(self, edition):
        return AfterSchoolRegistration.objects.of_edition(edition).count()

    @admin.action(description=gettext_lazy("Export family emails to CSV"))
    def download_families_emails(self, request, editions: QuerySet[AfterSchoolEdition]):
        families = []
        for edition in editions.all():
            for registration in edition.registrations.all():
                families.append(registration.child.family)
        emails_csv = FamilyEmailExporter(families).export_to_csv()
        return CsvHttpResponse('correos.csv', emails_csv)

    @admin.action(description=gettext_lazy("Download IDs of editions and registrations as JSON"))
    def download_ids_as_json(self, request, editions: QuerySet[AfterSchoolEdition]):
        ids = {}
        for edition in editions.all():
            ids[edition.id] = []
            for registration in edition.registrations.all():
                ids[edition.id].append(registration.id)
        file_name = f"editions_and_registrations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        file_content = json.dumps(ids, indent=4)
        return CsvHttpResponse(file_name, file_content)

    actions = [create_after_school_remittance, create_after_school_remittance_half, create_after_school_remittance_left,
               create_after_school_remittance_with_enrolment, download_families_emails, download_ids_as_json]


class AfterSchoolEditionInline(ReadOnlyTabularInline):
    model = AfterSchoolEdition
    fields = ['academic_course', 'after_school', 'code', 'timetable', 'period', 'levels', 'price_for_member',
              'price_for_no_member', 'registrations_link', 'edit_link']
    readonly_fields = ['edit_link', 'registrations_link']
    ordering = ['-academic_course', 'after_school']
    extra = 0

    @admin.display(description=_('Registrations'))
    def registrations_link(self, after_school_edition) -> str:
        registrations_count = AfterSchoolRegistration.objects.of_edition(after_school_edition).count()
        return Utils.get_model_link(
            model_name=AfterSchoolRegistration.__name__.lower(),
            link_text=str(registrations_count),
            filters=f'after_school_edition__id={after_school_edition.id}')

    @admin.display(description=_('Edit'))
    def edit_link(self, after_school_edition) -> str:
        return Utils.get_model_instance_link(AfterSchoolEdition.__name__.lower(), after_school_edition.id, _('Edit'))


class AfterSchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'funding', 'after_school_edition_count', 'after_school_registration_count', 'courses_count']
    ordering = ['name']
    list_filter = ['funding']
    inlines = [AfterSchoolEditionInline]
    search_fields = ['name']
    list_per_page = 35

    @admin.display(description=_('Editions'))
    def after_school_edition_count(self, after_school):
        return after_school.afterschooledition_set.count()

    @admin.display(description=_('Registrations'))
    def after_school_registration_count(self, after_school):
        return AfterSchoolRegistration.objects.filter(after_school_edition__after_school=after_school).count()

    @admin.display(description=_('Courses'))
    def courses_count(self, after_school):
        return distinct_count(AcademicCourse.objects.filter(afterschooledition__after_school=after_school))

    @admin.action(description=gettext_lazy("Merge activities (Move all editions to first selected)"))
    def merge_after_schools(self, request, after_school_activities: QuerySet[AfterSchool]):
        if after_school_activities.count() > 1:
            messages = []
            after_school_to_keep = after_school_activities.first()
            merged_name = after_school_to_keep.name

            messages.append(gettext_lazy('After-school kept') + f': {after_school_to_keep} ({after_school_to_keep.id})')
            for after_school in after_school_activities.all():
                if after_school.id != after_school_to_keep.id:
                    for edition in after_school.afterschooledition_set.all():
                        messages.append(
                            gettext_lazy('Edition changed') + f': {edition} ({edition.id}). ' +
                            gettext_lazy('After-school') + f': {edition.after_school.id} -> {after_school_to_keep.id}')
                        edition.after_school = after_school_to_keep
                        edition.save()

                    merged_name += f' | {after_school.name}'

                    messages.append(gettext_lazy('After-school deleted') + f': {after_school} ({after_school.id})')
                    after_school.delete()

            if after_school_to_keep.name != merged_name:
                messages.append(
                    gettext_lazy('After-school renamed') +
                    f': {after_school_to_keep.name} '
                    f'({after_school_to_keep.id}) -> {merged_name}')
                after_school_to_keep.name = merged_name
                after_school_to_keep.save()

            message = mark_safe('<br/>'.join(messages))
        else:
            message = gettext_lazy('No merge done. You have to select more than one after-school')
        self.message_user(request=request, message=message)

    actions = ['merge_after_schools']
