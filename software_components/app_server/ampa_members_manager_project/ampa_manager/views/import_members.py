from django.shortcuts import render

from ampa_manager.family.use_cases.importers.members_importer import MembersImporter
from ampa_manager.forms import ImportMembersForm
from ampa_manager.utils.string_utils import StringUtils


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
        'excel_columns': get_excel_columns(),
        'form_action': '/ampa/members/import/',
        'excel_template_file_name': 'templates/plantilla_importar_socios.xls'
    }
    return render(request, 'import_members.html', context)


def get_excel_columns():
    columns = []
    for column in MembersImporter.COLUMNS_TO_IMPORT:
        index = column[0]
        letter = StringUtils.get_excel_column_letter(index).upper()
        label = column[3]
        columns.append([letter, label])
    return columns
