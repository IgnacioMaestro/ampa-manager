from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from ampa_manager.forms import ImportMembersForm
from ampa_manager.management.commands.import_members import ImportMembersCommand
from ampa_manager.utils.string_utils import StringUtils


def import_members(request):
    context = {
        'excel_columns': get_excel_columns(),
        'form_action': '/ampa/import/members/',
        'importer_title': _('Import members'),
    }

    if request.method == 'POST':
        form = ImportMembersForm(request.POST, request.FILES)
        if form.is_valid():
            context['import_log'] = ImportMembersCommand.import_members_file(request.FILES['file'])
    else:
        form = ImportMembersForm()

    context['form'] = form
    return render(request, 'importer.html', context)

def get_excel_columns():
    columns = []
    for column in ImportMembersCommand.COLUMNS_TO_IMPORT:
        index = StringUtils.get_excel_column_letter(column[0]).upper()
        name = column[3]
        columns.append([index, name])
    return columns
