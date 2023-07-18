from django.shortcuts import render
from django.urls import reverse
from django.views import View

from ampa_manager.activity.models.camps.camps_edition import CampsEdition
from ampa_manager.activity.use_cases.importers.camps_importer import CampsImporter
from ampa_manager.forms import ImportCampsForm
from ampa_manager.utils.excel.importers_utils import get_excel_columns
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
            file_content = request.FILES['file'].read()
            import_info: ImportInfo = CampsImporter.import_camps_registrations(file_content, camps_edition)
            context = cls.__create_context_with_import_info(form, import_info)
        else:
            context = cls.__create_context_with_processed_form(form)
        return render(request, cls.TEMPLATE, context)

    @classmethod
    def get(cls, request):
        context = cls.__create_context_with_empty_form()
        return render(request, cls.TEMPLATE, context)

    @classmethod
    def __create_context_with_import_info(cls, form: ImportCampsForm, import_info: ImportInfo) -> dict:
        context = {
            'form': form,
            'success': import_info.success(),
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
            'excel_columns': get_excel_columns(CampsImporter.COLUMNS_TO_IMPORT),
            'form_action': reverse(cls.ENDPOINT),
            'excel_template_file_name': 'templates/plantilla_importar_campamentos.xls'
        }
