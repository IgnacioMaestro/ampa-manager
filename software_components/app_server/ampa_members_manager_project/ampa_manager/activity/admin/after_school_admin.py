from django.contrib import admin
from django.db.models import QuerySet
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django import forms

from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.charge.use_cases.after_school.after_school_remittance_creator.after_school_remittance_creator import \
    AfterSchoolRemittanceCreator
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.read_only_inline import ReadOnlyTabularInline


class AfterSchoolRegistrationAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['holder'].queryset = Holder.objects.of_family(self.instance.child.family)
        else:
            self.fields['holder'].queryset = Holder.objects.none()


class AfterSchoolRegistrationAdmin(admin.ModelAdmin):
    list_display = ['after_school_edition', 'child', 'holder']
    ordering = ['after_school_edition__after_school__name', 'after_school_edition']
    list_filter = ['after_school_edition__academic_course__initial_year',
                   'after_school_edition__period',
                   'after_school_edition__timetable',
                   'after_school_edition__levels',
                   'after_school_edition__after_school__name']
    search_fields = ['child__name', 'child__family__surnames', 'after_school_edition__after_school__name',
                     'holder__bank_account__iban',
                     'holder__parent__name_and_surnames']
    list_per_page = 25
    form = AfterSchoolRegistrationAdminForm


class AfterSchoolRegistrationInline(ReadOnlyTabularInline):
    model = AfterSchoolRegistration
    list_display = ['after_school_edition', 'child', 'holder']
    ordering = ['after_school_edition__after_school__name', 'after_school_edition']
    extra = 0


class AfterSchoolEditionAdmin(admin.ModelAdmin):
    inlines = [AfterSchoolRegistrationInline]
    list_display = ['academic_course', 'after_school', 'price_for_member', 'price_for_no_member', 'after_schools_count']
    ordering = ['-academic_course', 'after_school']
    list_filter = ['academic_course__initial_year', 'after_school__name']
    search_fields = ['after_school__name']
    list_per_page = 25

    @admin.action(description=_("Create after school remittance"))
    def create_after_school_remittance(self, request, after_school_editions: QuerySet[AfterSchoolEdition]):
        after_school_remittance = AfterSchoolRemittanceCreator(after_school_editions).create_full()
        url = after_school_remittance.get_admin_url()
        message = mark_safe(
            _("Activity remittance created") + " (<a href=\"" + url + "\">" + _("View details") + "</a>)")
        return self.message_user(request=request, message=message)

    @admin.action(description=_("Create after school remittance with half"))
    def create_after_school_remittance_half(self, request, after_school_editions: QuerySet[AfterSchoolEdition]):
        after_school_remittance = AfterSchoolRemittanceCreator(after_school_editions).create_half()
        url = after_school_remittance.get_admin_url()
        message = mark_safe(
            _("Activity remittance created") + " (<a href=\"" + url + "\">" + _("View details") + "</a>)")
        return self.message_user(request=request, message=message)

    @admin.action(description=_("Create after school remittance with left"))
    def create_after_school_remittance_left(self, request, after_school_editions: QuerySet[AfterSchoolEdition]):
        after_school_remittance = AfterSchoolRemittanceCreator(after_school_editions).create_left()
        url = after_school_remittance.get_admin_url()
        message = mark_safe(
            _("Activity remittance created") + " (<a href=\"" + url + "\">" + _("View details") + "</a>)")
        return self.message_user(request=request, message=message)

    @admin.display(description=_('Registrations'))
    def after_schools_count(self, edition):
        return AfterSchoolRegistration.objects.of_edition(edition).count()

    actions = [create_after_school_remittance, create_after_school_remittance_half, create_after_school_remittance_left]


class AfterSchoolEditionInline(admin.TabularInline):
    model = AfterSchoolEdition
    list_display = ['after_school', 'price_for_member', 'price_for_no_member', 'academic_course']
    ordering = ['-academic_course', 'after_school']
    extra = 0


class AfterSchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'funding', 'after_school_edition_count']
    ordering = ['name']
    list_filter = ['funding']
    inlines = [AfterSchoolEditionInline]
    search_fields = ['name']
    list_per_page = 35

    @admin.display(description=_('Editions'))
    def after_school_edition_count(self, after_school):
        return after_school.afterschooledition_set.count()
