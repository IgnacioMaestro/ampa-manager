from django.shortcuts import render

from ampa_manager.family.use_cases.importers.members_importer import MembersImporter
from ampa_manager.forms import ImportMembersForm
from ampa_manager.utils.excel.importers_utils import get_excel_columns


def import_members(request):
    success = None
    results = None
    summary = None

    if request.method == 'POST':
        form = ImportMembersForm(request.POST, request.FILES)
        if form.is_valid():
            total_rows, success_rows, summary, results = \
                MembersImporter.import_members(file_content=request.FILES['file'].read())
            success = total_rows > 0 and total_rows == success_rows
    else:
        form = ImportMembersForm()

    context = {
        'form': form,
        'success': success,
        'import_results': results,
        'import_summary': summary,
        'excel_columns': get_excel_columns(MembersImporter.COLUMNS_TO_IMPORT),
        'form_action': '/ampa/members/import/',
        'excel_template_file_name': 'templates/plantilla_importar_socios.xls'
    }
    return render(request, 'import_members.html', context)
