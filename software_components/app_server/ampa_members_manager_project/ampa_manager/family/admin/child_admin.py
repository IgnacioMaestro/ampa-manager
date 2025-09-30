from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _, gettext_lazy
from openpyxl.workbook import Workbook

from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.academic_course.models.level import Level
from ampa_manager.activity.admin.after_school_admin import AfterSchoolRegistrationInline
from ampa_manager.activity.admin.camps_admin import CampsRegistrationInline
from ampa_manager.activity.admin.custody_admin import CustodyRegistrationInline
from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.activity.models.camps.camps_registration import CampsRegistration
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.family.admin.filters.child_filters import ChildCycleFilter, ChildLevelListFilter, ChildIsMemberFilter
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.membership import Membership


class ChildAdmin(admin.ModelAdmin):
    list_display = ['name', 'family', 'after_school_registrations', 'custody_registrations',
                    'camps_registrations', 'year_of_birth', 'child_course', 'is_member']
    fields = ['name', 'family', 'parents', 'year_of_birth', 'repetition', 'created', 'modified']
    readonly_fields = ['created', 'modified', 'parents']
    ordering = ['name']
    list_filter = [ChildIsMemberFilter, ChildCycleFilter, ChildLevelListFilter, 'year_of_birth', 'repetition']
    search_fields = ['name', 'normalized_name', 'year_of_birth', 'family__surnames', 'family__normalized_surnames',
                     'id']
    list_per_page = 25
    inlines = [AfterSchoolRegistrationInline, CustodyRegistrationInline, CampsRegistrationInline]
    autocomplete_fields = ['family']

    @admin.display(description=_('Is member'))
    def is_member(self, child):
        return _('Yes') if Membership.is_member_child(child) else _('No')

    @admin.display(description=_('Course'))
    def child_course(self, child):
        return Level.get_level_name(child.level)

    @admin.display(description=_('Parents'))
    def parents(self, child):
        return ', '.join(p.name_and_surnames for p in child.family.parents.all())

    @admin.display(description=_('After-sch.'))
    def after_school_registrations(self, child):
        active_course = AfterSchoolRegistration.objects.of_child(child).of_active_course().count()
        previous_courses = AfterSchoolRegistration.objects.of_child(child).of_previous_courses().count()
        return f'{active_course} / {previous_courses}'

    @admin.display(description=_('Cust.'))
    def custody_registrations(self, child):
        active_course = CustodyRegistration.objects.of_child(child).of_active_course().count()
        previous_courses = CustodyRegistration.objects.of_child(child).of_previous_courses().count()
        return f'{active_course} / {previous_courses}'

    @admin.display(description=_('Cmps.'))
    def camps_registrations(self, child):
        active_course = CampsRegistration.objects.of_child(child).of_active_course().count()
        previous_courses = CampsRegistration.objects.of_child(child).of_previous_courses().count()
        return f'{active_course} / {previous_courses}'

    @admin.display(description=_('Parents'))
    def parents(self, child):
        return ', '.join([str(p) for p in child.family.parents.all()])

    @admin.action(description=gettext_lazy("Export children to XLS"))
    def export_children_xls(self, _, children: QuerySet[Child]):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',)
        response['Content-Disposition'] = 'attachment; filename=alumnos.xlsx'
        wb = Workbook()
        ws = wb.active

        column_titles = ['Nombre', 'Apellidos', 'Curso']
        ws.append(column_titles)

        for child in children:
            ws.append([
                child.name.encode('utf-8'),
                child.family.surnames.encode('utf-8'),
                child.level
            ])

        wb.save(response)

        return response

    actions = [export_children_xls]
