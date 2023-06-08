from django.shortcuts import render
from django.urls import reverse
from django.views import View

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.activity.use_cases.importers.custody_importer import CustodyImporter
from ampa_manager.forms import ImportCustodyForm
from ampa_manager.utils.excel.importers_utils import get_excel_columns
from ampa_manager.views.import_info import ImportInfo


class ImportCustodyView(View):
    http_method_names = ['post', 'get']
    TEMPLATE = 'import_custody.html'

    @classmethod
    def post(cls, request):
        form = ImportCustodyForm(request.POST, request.FILES)
        if form.is_valid():
            edition_id = request.POST.get('custody_edition')
            custody_edition = CustodyEdition.objects.get(id=edition_id)
            file_content = request.FILES['file'].read()
            import_info: ImportInfo = CustodyImporter.import_custody(file_content, custody_edition)
            context = cls.__create_context_with_import_info(form, import_info)
        else:
            context = cls.__create_context_with_processed_form(form)
        return render(request, cls.TEMPLATE, context)

    @classmethod
    def get(cls, request):
        context = cls.__create_context_with_empty_form()
        return render(request, cls.TEMPLATE, context)

    @classmethod
    def __create_context_with_import_info(cls, form: ImportCustodyForm, import_info: ImportInfo) -> dict:
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
        return cls.__create_context_with_form(ImportCustodyForm())

    @classmethod
    def __create_context_with_form(cls, form) -> dict:
        context = {
            'form': form,
            'success': None,
            'import_results': None,
            'import_summary': None
        }
        context.update(cls.__create_context_fix_part())
        return context

    @classmethod
    def __create_context_fix_part(cls) -> dict:
        return {
            'excel_columns': get_excel_columns(CustodyImporter.COLUMNS_TO_IMPORT),
            'form_action': reverse('import_custody'),
            'excel_template_file_name': 'templates/plantilla_importar_ludoteca.xls'
        }
