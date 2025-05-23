from typing import Optional

from django.db import transaction
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View

from ampa_manager.activity.use_cases.importers.after_school_activities_importer import AfterSchoolsActivitiesImporter
from ampa_manager.activity.use_cases.importers.import_excel_result import ImportExcelResult
from ampa_manager.forms import ImportAfterSchoolsRegistrationsForm, ImportAfterSchoolsActivitiesForm
from ampa_manager.views.import_custody_view import SimulationException


class ImportAfterSchoolActivitiesView(View):
    HTML_TEMPLATE = 'import_after_school_activities.html'
    EXCEL_TEMPLATE = 'templates/plantilla_importar_extraescolares.xlsx'
    IMPORTER_TITLE = _('Import afterschool activities')
    VIEW_NAME = 'import_after_schools_activities'

    @classmethod
    def get_context(cls, form: Optional[ImportAfterSchoolsRegistrationsForm] = None) -> dict:
        if not form:
            form = ImportAfterSchoolsActivitiesForm()

        return {
            'form': form,
            'importer_title': cls.IMPORTER_TITLE,
            'view_url': reverse(cls.VIEW_NAME),
            'excel_columns': AfterSchoolsActivitiesImporter.COLUMNS_TO_IMPORT,
            'excel_template_file_name': cls.EXCEL_TEMPLATE
        }

    @classmethod
    def get(cls, request):
        return render(request, cls.HTML_TEMPLATE, cls.get_context())

    @classmethod
    def post(cls, request):
        form = ImportAfterSchoolsActivitiesForm(request.POST, request.FILES)
        context = cls.get_context(form)

        if form.is_valid():
            result: ImportExcelResult = cls.import_after_school_activities(
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
    def import_after_school_activities(cls, excel_content, simulation: bool) -> Optional[ImportExcelResult]:
        result = None
        try:
            with transaction.atomic():
                result = AfterSchoolsActivitiesImporter(excel_content).run()

                if simulation:
                    raise SimulationException()
        except SimulationException:
            print('Simulation mode: changes rolled back')

        return result
