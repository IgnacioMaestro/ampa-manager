from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from ampa_manager.forms import ImportMembersForm
from ampa_manager.management.commands.import_members import Command as ImportMembersCommand
from ampa_manager.utils.string_utils import StringUtils


def import_members(request):
    import_log = None

    if request.method == 'POST':
        form = ImportMembersForm(request.POST, request.FILES)
        if form.is_valid():
            logs = ImportMembersCommand.import_members_file(file_content=request.FILES['file'].read())
            import_log = '\n'.join(logs)
    else:
        form = ImportMembersForm()

    context = {
        'form': form,
        'import_log': import_log,
        'excel_columns': get_excel_columns(),
        'form_action': '/ampa/members/import/',
        'importer_title': _('Import members'),
        'excel_template_file_name': 'plantilla_importar_socios.xls'
    }
    return render(request, 'importer.html', context)

def get_excel_columns():
    columns = []
    for column in ImportMembersCommand.COLUMNS_TO_IMPORT:
        index = StringUtils.get_excel_column_letter(column[0]).upper()
        name = column[3]
        columns.append([index, name])
    return columns
