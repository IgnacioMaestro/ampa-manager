from django.shortcuts import render
from django.urls import reverse
from django.views import View

from ampa_manager.family.use_cases.importers.members_importer import MembersImporter
from ampa_manager.forms import ImportMembersForm
from ampa_manager.utils.excel.importers_utils import get_excel_columns
from ampa_manager.views.import_info import ImportInfo


class ImportMembers(View):
    TEMPLATE = 'import_members.html'

    @classmethod
    def post(cls, request):
        form = ImportMembersForm(request.POST, request.FILES)
        if form.is_valid():
            file_content = request.FILES['file'].read()
            import_info: ImportInfo = MembersImporter.import_members(file_content=file_content)
            context = cls.__create_context_with_import_info(form, import_info)
        else:
            context = cls.__create_context_with_processed_form(form)
        return render(request, cls.TEMPLATE, context)

    @classmethod
    def get(cls, request):
        context = cls.__create_context_with_empty_form()
        return render(request, cls.TEMPLATE, context)

    @classmethod
    def __create_context_with_import_info(cls, form: ImportMembersForm, import_info: ImportInfo) -> dict:
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
        return cls.__create_context_with_form(ImportMembersForm())

    @classmethod
    def __create_context_with_form(cls, form) -> dict:
        context = {'form': form}
        context.update(cls.__create_context_fix_part())
        return context

    @classmethod
    def __create_context_fix_part(cls) -> dict:
        return {
            'excel_columns': get_excel_columns(MembersImporter.COLUMNS_TO_IMPORT),
            'form_action': reverse('import_members'),
            'excel_template_file_name': 'templates/plantilla_importar_socios.xls'
        }
