from typing import Optional

from django.db import transaction
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.activity.use_cases.importers.custody_importer import CustodyImporter
from ampa_manager.activity.use_cases.importers.import_excel_result import ImportExcelResult
from ampa_manager.forms import ImportCustodyForm


class SimulationException(Exception):
    pass


class ImportCustody(View):
    HTML_TEMPLATE = 'import_custody.html'
    EXCEL_TEMPLATE = 'templates/plantilla_importar_ludoteca.xls'
    IMPORTER_TITLE = _('Import custody')
    VIEW_NAME = 'import_custody'

    @classmethod
    def get_context(cls, form: Optional[ImportCustodyForm] = None) -> dict:
        if not form:
            form = ImportCustodyForm()

        return {
            'form': form,
            'importer_title': cls.IMPORTER_TITLE,
            'view_url': reverse(cls.VIEW_NAME),
            'excel_columns': CustodyImporter.COLUMNS_TO_IMPORT,
            'excel_template_file_name': cls.EXCEL_TEMPLATE
        }

    @classmethod
    def get(cls, request):
        return render(request, cls.HTML_TEMPLATE, cls.get_context())

    @classmethod
    def post(cls, request):
        form = ImportCustodyForm(request.POST, request.FILES)
        context = cls.get_context(form)

        if form.is_valid():
            result: ImportExcelResult = cls.import_custody(
                excel_content=request.FILES['file'].read(),
                edition_id=request.POST.get('custody_edition'),
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
    def import_custody(cls, excel_content, edition_id: int, simulation: bool) -> Optional[ImportExcelResult]:
        result = None
        try:
            with transaction.atomic():
                edition = CustodyEdition.objects.get(id=edition_id)
                result = CustodyImporter(excel_content, edition).run()

                if simulation:
                    raise SimulationException()
        except SimulationException:
            print('Simulation mode: changes rolled back')

        return result
