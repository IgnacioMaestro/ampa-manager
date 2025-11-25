from typing import Optional

from django.db import transaction
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View

from ampa_manager.activity.use_cases.importers.after_schools_importer import AfterSchoolsImporter
from ampa_manager.activity.use_cases.importers.import_excel_result import ImportExcelResult
from ampa_manager.forms.import_after_schools_registrations_form import ImportAfterSchoolsRegistrationsForm
from ampa_manager.views.importers.import_custody_view import SimulationException


class ImportAfterSchoolRegistrationsView(View):
    HTML_TEMPLATE = 'importers/import_after_school_registrations.html'
    EXCEL_TEMPLATE = 'templates/plantilla_importar_extraescolares.xlsx'
    IMPORTER_TITLE = _('Import afterschool registrations')
    VIEW_NAME = 'import_after_schools_registrations'

    @classmethod
    def get_context(cls, form: Optional[ImportAfterSchoolsRegistrationsForm] = None) -> dict:
        if not form:
            form = ImportAfterSchoolsRegistrationsForm()

        return {
            'form': form,
            'importer_title': cls.IMPORTER_TITLE,
            'view_url': reverse(cls.VIEW_NAME),
            'excel_columns': AfterSchoolsImporter.COLUMNS_TO_IMPORT,
            'excel_template_file_name': cls.EXCEL_TEMPLATE
        }

    @classmethod
    def get(cls, request):
        return render(request, cls.HTML_TEMPLATE, cls.get_context())

    @classmethod
    def post(cls, request):
        form = ImportAfterSchoolsRegistrationsForm(request.POST, request.FILES)
        context = cls.get_context(form)

        if form.is_valid():
            result: ImportExcelResult = cls.import_after_school_registrations(
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
    def import_after_school_registrations(cls, excel_content, simulation: bool) -> Optional[ImportExcelResult]:
        result = None
        try:
            with transaction.atomic():
                result = AfterSchoolsImporter(excel_content).run()

                if simulation:
                    raise SimulationException()
        except SimulationException:
            print('Simulation mode: changes rolled back')

        return result
