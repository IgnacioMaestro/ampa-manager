from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from ampa_manager.forms import ImportMembersForm
from ampa_manager.management.commands.import_custody import Command as ImportCustody
from ampa_manager.utils.string_utils import StringUtils


def import_custody(request):
    import_log = None

    if request.method == 'POST':
        form = ImportMembersForm(request.POST, request.FILES)
        if form.is_valid():
            logs = ImportCustody.import_custody_file(file_content=request.FILES['file'].read())
            import_log = '\n'.join(logs)
    else:
        form = ImportMembersForm()

    context = {
        'form': form,
        'import_log': import_log,
        'excel_columns': get_excel_columns(),
        'form_action': '/ampa/custody/import/',
        'importer_title': _('Import custody'),
        'excel_template_file_name': 'templates/plantilla_importar_ludoteca.xls'
    }
    return render(request, 'importer.html', context)

def get_excel_columns():
    columns = []
    for column in ImportCustody.COLUMNS_TO_IMPORT:
        index = StringUtils.get_excel_column_letter(column[0]).upper()
        name = column[3]
        columns.append([index, name])
    return columns
