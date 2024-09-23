from typing import Optional

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from ampa_manager.activity.models.camps.camps_edition import CampsEdition
from ampa_manager.activity.use_cases.importers.base_importer import BaseImporter
from ampa_manager.activity.use_cases.old_importers.camps_importer import CampsImporter
from ampa_manager.forms import ImportCampsForm
from ampa_manager.views.import_custody import SimulationException
from ampa_manager.views.import_info import ImportInfo


class ImportCamps(View):
    TEMPLATE = 'import_camps.html'
    ENDPOINT = 'import_camps'

    @classmethod
    def post(cls, request):
        form = ImportCampsForm(request.POST, request.FILES)
        if form.is_valid():
            edition_id = request.POST.get('camps_edition')
            camps_edition = CampsEdition.objects.get(id=edition_id)
            uploaded_file: UploadedFile = request.FILES['file']
            file_content = uploaded_file.read()
            simulation = request.POST.get('simulation')

            import_info: ImportInfo = cls.import_camps_registrations(file_content, camps_edition, simulation)
            context = cls.__create_context_with_import_info(form, import_info, simulation)
        else:
            context = cls.__create_context_with_processed_form(form)
        return render(request, cls.TEMPLATE, context)

    @classmethod
    def import_camps_registrations(cls, file_content, camps_edition: CampsEdition, simulation: bool) -> Optional[ImportInfo]:
        import_info: Optional[ImportInfo] = None
        try:
            with transaction.atomic():
                import_info: ImportInfo = CampsImporter.import_camps_registrations(file_content, camps_edition)

                if simulation:
                    raise SimulationException()
        except SimulationException:
            print('Simulation mode: changes rolled back')

        return import_info

    @classmethod
    def get(cls, request):
        context = cls.__create_context_with_empty_form()
        return render(request, cls.TEMPLATE, context)

    @classmethod
    def __create_context_with_import_info(cls, form: ImportCampsForm, import_info: ImportInfo,
                                          simulation: bool) -> dict:
        context = {
            'form': form,
            'success': import_info.success(),
            'simulation': simulation,
            'import_results': import_info.results,
            'import_summary': import_info.summary,
        }
        context.update(cls.__create_context_fix_part())
        return context

    @classmethod
    def __create_context_with_processed_form(cls, form) -> dict:
        return cls.__create_context_with_form(form)

    @classmethod
    def __create_context_with_empty_form(cls) -> dict:
        return cls.__create_context_with_form(ImportCampsForm())

    @classmethod
    def __create_context_with_form(cls, form) -> dict:
        context = {'form': form}
        context.update(cls.__create_context_fix_part())
        return context

    @classmethod
    def __create_context_fix_part(cls) -> dict:
        return {
            'excel_columns': BaseImporter.get_excel_columns(CampsImporter.COLUMNS_TO_IMPORT),
            'form_action': reverse(cls.ENDPOINT),
            'excel_template_file_name': 'templates/plantilla_importar_campamentos.xls'
        }
