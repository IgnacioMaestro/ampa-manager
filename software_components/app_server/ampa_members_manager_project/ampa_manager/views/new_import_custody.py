from django.core.files.uploadedfile import UploadedFile
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.activity.use_cases.importers.base_importer import BaseImporter
from ampa_manager.activity.use_cases.old_importers.excel.titled_list import TitledList
from ampa_manager.forms import ImportCustodyForm
from ampa_manager.importation.use_cases.custody_importer.custody_importer import CustodyImporter
from ampa_manager.views.import_info import ImportInfo


class NewImportCustody(View):
    TEMPLATE = 'import_custody.html'

    @classmethod
    def post(cls, request):
        form = ImportCustodyForm(request.POST, request.FILES)
        if form.is_valid():
            edition_id = request.POST.get('custody_edition')
            custody_edition = CustodyEdition.objects.get(id=edition_id)
            uploaded_file: UploadedFile = request.FILES['file']
            file_content = uploaded_file.read()
            file_name = uploaded_file.name
            CustodyImporter(file_name, file_content, custody_edition).import_custody()
            import_info = ImportInfo(0, 0, TitledList('example'), TitledList('example'))
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
        context = {'form': form}
        context.update(cls.__create_context_fix_part())
        return context

    @classmethod
    def __create_context_fix_part(cls) -> dict:
        return {
            'excel_columns': BaseImporter.get_excel_columns(CustodyImporter.COLUMNS_TO_IMPORT),
            'form_action': reverse('import_custody'),
            'excel_template_file_name': 'templates/plantilla_importar_ludoteca.xls'
        }
