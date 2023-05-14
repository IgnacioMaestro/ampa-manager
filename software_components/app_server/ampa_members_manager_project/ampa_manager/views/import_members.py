from django.shortcuts import render

from ampa_manager.family.use_cases.importers.members_importer import MembersImporter
from ampa_manager.forms import ImportMembersForm
from ampa_manager.utils.importers_utils import get_excel_columns


def import_members(request):
    import_log = None

    if request.method == 'POST':
        form = ImportMembersForm(request.POST, request.FILES)
        if form.is_valid():
            logs = MembersImporter.import_members(file_content=request.FILES['file'].read())
            import_log = '\n'.join(logs)
    else:
        form = ImportMembersForm()

    context = {
        'form': form,
        'import_log': import_log,
        'excel_columns': get_excel_columns(MembersImporter.COLUMNS_TO_IMPORT),
        'form_action': '/ampa/members/import/',
        'excel_template_file_name': 'templates/plantilla_importar_socios.xls'
    }
    return render(request, 'import_members.html', context)
