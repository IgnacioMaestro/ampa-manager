from django.core.files.uploadedfile import UploadedFile
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.forms import ImportCustodyForm
from ampa_manager.importation.models.custody_importation import CustodyImportation
from ampa_manager.importation.use_cases.custody_importation_view_utils import CustodyImportationViewUtils
from ampa_manager.importation.use_cases.custody_importer.custody_importer import CustodyImporter
from ampa_manager.importation.use_cases.custody_importer.rows_importer.errors_in_row import ErrorsInRow
from ampa_manager.utils.excel.titled_list import TitledList
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
            custody_importation: CustodyImportation
            errors: list[ErrorsInRow]
            custody_importation, errors = CustodyImporter(file_name, file_content, custody_edition).import_custody()
            import_info = cls.__create_import_info(custody_importation, errors)
            context = cls.__create_context_with_import_info(form, import_info)
        else:
            context = cls.__create_context_with_processed_form(form)
        return render(request, cls.TEMPLATE, context)

    @classmethod
    def __create_import_info(cls, custody_importation, errors):
        if errors is None:
            import_info = cls.__create_import_info_correct(custody_importation)
        else:
            import_info = cls.__create_import_info_errors(errors)
        return import_info

    @classmethod
    def __create_import_info_errors(cls, errors_in_rows: list[ErrorsInRow]):
        errors_summary: TitledList = TitledList('Errors')
        for errors_in_row in errors_in_rows:
            errors_in_row_summary = TitledList('Row number: ' + str(errors_in_row.get_row_number()))
            for row_error in errors_in_row.get_errors():
                errors_in_row_summary.append_element(str(row_error))
            errors_summary.append_sublist(errors_in_row_summary)
        import_info = ImportInfo(0, 0, errors_summary, TitledList(''))
        return import_info

    @classmethod
    def __create_import_info_correct(cls, custody_importation):
        number_of_rows = CustodyImportationViewUtils(custody_importation).get_number_of_rows()
        summary: TitledList = CustodyImportationViewUtils(custody_importation).get_summary()
        import_info = ImportInfo(number_of_rows, number_of_rows, summary, TitledList(''))
        return import_info

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
            # 'excel_columns': get_excel_columns(CustodyImporter.COLUMNS_TO_IMPORT),
            'form_action': reverse('new_import_custody'),
            'excel_template_file_name': 'templates/plantilla_importar_ludoteca.xls'
        }
