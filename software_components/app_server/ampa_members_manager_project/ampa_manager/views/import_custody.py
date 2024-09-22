from typing import Optional

from django.db import transaction
from django.shortcuts import render
from django.views import View

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.activity.use_cases.importers.custody_importer import CustodyImporter
from ampa_manager.activity.use_cases.importers.import_result import ImportResult
from ampa_manager.forms import ImportCustodyForm


class SimulationException(Exception):
    pass


class ImportCustody(View):
    HTML_TEMPLATE = 'import_custody.html'
    EXCEL_TEMPLATE = 'templates/plantilla_importar_ludoteca.xls'

    @classmethod
    def post(cls, request):
        context = {}
        form = ImportCustodyForm(request.POST, request.FILES)

        if form.is_valid():
            result: Optional[ImportResult] = cls.import_custody(
                excel_content=request.FILES['file'].read(),
                edition_id=request.POST.get('custody_edition'),
                simulation=request.POST.get('simulation')
            )

            context['result'] = {}
            context['result']['success'] = result.success
            context['result']['rows'] = result.rows

        context['form'] = form
        context['excel_columns'] = CustodyImporter.get_excel_columns(CustodyImporter.COLUMNS_TO_IMPORT)
        context['excel_template_file_name'] = cls.EXCEL_TEMPLATE
        context['simulation'] = request.POST.get('simulation')

        return render(request, cls.HTML_TEMPLATE, context)

    @classmethod
    def import_custody(cls, excel_content, edition_id: int, simulation: bool) -> Optional[ImportResult]:
        result = None
        try:
            with transaction.atomic():
                edition = CustodyEdition.objects.get(id=edition_id)
                result = CustodyImporter(excel_content, edition).import_custody()

                if simulation:
                    raise SimulationException()
        except SimulationException:
            print('Simulation mode: changes rolled back')

        return result
