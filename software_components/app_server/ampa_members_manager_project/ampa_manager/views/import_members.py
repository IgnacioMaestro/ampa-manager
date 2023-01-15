from django.http import HttpResponseRedirect
from django.shortcuts import render

from ampa_manager.forms import ImportMembersForm
from ampa_manager.management.commands.import_members import ImportMembersCommand


def import_members(request):
    context = {
        'excel_columns': get_excel_columns(),
    }

    if request.method == 'POST':
        form = ImportMembersForm(request.POST, request.FILES)
        if form.is_valid():
            context['import_log'] = ImportMembersCommand.import_members_file(request.FILES['file'])
    else:
        form = ImportMembersForm()

    context['form'] = form
    return render(request, 'import_members.html', context)

def get_excel_columns():
    columns = []
    for column in ImportMembersCommand.COLUMNS_TO_IMPORT:
        index = column[0] + 1
        name = column[2].replace('_', ' ').upper()
        columns.append([index, name])
    return columns
