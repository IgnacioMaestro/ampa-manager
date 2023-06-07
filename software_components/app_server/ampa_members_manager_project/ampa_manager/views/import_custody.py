from django.shortcuts import render

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.activity.use_cases.importers.custody_importer import CustodyImporter
from ampa_manager.forms import ImportCustodyForm
from ampa_manager.utils.excel.importers_utils import get_excel_columns
from ampa_manager.views.import_info import ImportInfo

CONTEXT_FIX_PART = {
    'excel_columns': get_excel_columns(CustodyImporter.COLUMNS_TO_IMPORT),
    'form_action': '/ampa/custody/import/',
    'excel_template_file_name': 'templates/plantilla_importar_ludoteca.xls'
}


def import_custody(request):
    if request.method == 'POST':
        form = ImportCustodyForm(request.POST, request.FILES)
        if form.is_valid():
            edition_id = request.POST.get('custody_edition')
            custody_edition = CustodyEdition.objects.get(id=edition_id)
            file_content = request.FILES['file'].read()
            import_info: ImportInfo = CustodyImporter.import_custody(file_content, custody_edition)
            context = create_full_context(form, import_info)
        else:
            context = create_context_only_with_form(form)
    else:
        form = ImportCustodyForm()
        context = create_context_only_with_form(form)
    return render(request, 'import_custody.html', context)


def create_full_context(form: ImportCustodyForm, import_info: ImportInfo):
    context = {
        'form': form,
        'success': import_info.success(),
        'import_results': import_info.results,
        'import_summary': import_info.summary,
    }
    context.update(CONTEXT_FIX_PART)
    return context


def create_context_only_with_form(form):
    context = {
        'form': form,
        'success': None,
        'import_results': None,
        'import_summary': None,
    }
    context.update(CONTEXT_FIX_PART)
    return context
