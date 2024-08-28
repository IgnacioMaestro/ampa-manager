from typing import Optional

from django.db import transaction
from django.shortcuts import render
from django.views import View

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.activity.use_cases.importers.custody_importer import CustodyImporter
from ampa_manager.activity.use_cases.importers.excel_manager import ImportSummary
from ampa_manager.forms import ImportCustodyForm
from ampa_manager.utils.excel.importers_utils import get_excel_columns


class SimulationException(Exception):
    pass


class ImportCustody(View):
    TEMPLATE = 'import_custody.html'
    EXCEL_TEMPLATE = 'templates/plantilla_importar_ludoteca.xls'

    @classmethod
    def post(cls, request):
        context = {}
        form = ImportCustodyForm(request.POST, request.FILES)

        if form.is_valid():
            import_summary: Optional[ImportSummary] = cls.import_custody(
                excel_content=request.FILES['file'].read(),
                edition_id=request.POST.get('custody_edition'),
                simulation=request.POST.get('simulation')
            )

            context['success'] = import_summary.success()
            context['import_results'] = import_summary.results
            context['import_summary'] = import_summary.summary
            context['simulation'] = request.POST.get('simulation')

        context['form'] = form
        context['excel_columns'] = get_excel_columns(CustodyImporter.COLUMNS_TO_IMPORT)
        context['excel_template_file_name'] = cls.EXCEL_TEMPLATE
        return render(request, cls.TEMPLATE, context)

    @classmethod
    def import_custody(cls, excel_content, edition_id: int, simulation: bool) -> Optional[ImportSummary]:
        import_summary = None
        try:
            with transaction.atomic():
                edition = CustodyEdition.objects.of_current_academic_course().get(id=edition_id)
                import_summary = CustodyImporter(excel_content, edition).import_custody()

                if simulation:
                    raise SimulationException()
        except SimulationException:
            print('Simulation mode: changes rolled back')

        return import_summary
