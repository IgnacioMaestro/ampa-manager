from typing import Optional

from django.db import transaction
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.activity.use_cases.importers.import_excel_result import ImportExcelResult
from ampa_manager.activity.use_cases.importers.members_importer import MembersImporter
from ampa_manager.charge.models.fee.fee import Fee
from ampa_manager.family.models.membership import Membership
from ampa_manager.forms import ImportMembersForm
from ampa_manager.views.import_custody_view import SimulationException


class GenerateMembersRemittanceView(View):
    HTML_TEMPLATE = 'generate_members_remittance.html'
    VIEW_NAME = 'generate_members_remittance'

    @classmethod
    def get_context(cls, form: Optional[ImportMembersForm] = None) -> dict:
        if not form:
            form = ImportMembersForm()

        active_course = cls.get_active_course()
        last_course = cls.get_last_course()
        return {
            'form': form,
            'view_url': reverse(cls.VIEW_NAME),
            'title': _('Generate members remittance'),
            'active_course': '25-26',
            'active_course_members_count': cls.get_members_count(active_course),
            'last_course_members_count': cls.get_members_count(last_course),
            'active_course_fee': cls.get_course_fee(active_course),
            'last_course_fee': cls.get_course_fee(last_course),
        }

    @classmethod
    def get_members_count(cls, course: Optional[AcademicCourse]) -> int:
        if not course:
            return 0
        return Membership.objects.of_course(course).count()

    @classmethod
    def get_active_course(cls) -> AcademicCourse:
        return ActiveCourse.load()

    @classmethod
    def get_last_course(cls) -> AcademicCourse:
        active_course = cls.get_active_course()
        return AcademicCourse.objects.get(initial_year=active_course.initial_year-1)

    @classmethod
    def get_course_fee(cls, course: Optional[AcademicCourse]) -> int:
        try:
            return Fee.objects.get(academic_course=course).amount
        except Fee.DoesNotExist:
            return 0

    @classmethod
    def get(cls, request):
        return render(request, cls.HTML_TEMPLATE, cls.get_context())

    @classmethod
    def post(cls, request):
        form = ImportMembersForm(request.POST, request.FILES)
        context = cls.get_context(form)

        if form.is_valid():
            result: ImportExcelResult = cls.import_members(
                excel_content=request.FILES['file'].read(),
                simulation=request.POST.get('simulation')
            )

            context['result'] = {
                'rows': result.rows,
                'state': result.state,
                'rows_summary': {
                    'total': result.rows_total,
                    'with_data': result.rows_with_data,
                    'without_data': result.rows_without_data,
                    'imported_ok': result.rows_imported_ok,
                    'imported_warning': result.rows_imported_warning,
                    'not_imported': result.rows_not_imported,
                },
            }

        context['simulation'] = request.POST.get('simulation')
        return render(request, cls.HTML_TEMPLATE, context)

    @classmethod
    def import_members(cls, excel_content, simulation: bool) -> Optional[ImportExcelResult]:
        result = None
        try:
            with transaction.atomic():
                result = MembersImporter(excel_content).run()

                if simulation:
                    raise SimulationException()
        except SimulationException:
            print('Simulation mode: changes rolled back')

        return result
