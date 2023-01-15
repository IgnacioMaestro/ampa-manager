from django.http import HttpResponseRedirect
from django.shortcuts import render

from ampa_manager.forms import ImportMembersForm
from ampa_manager.management.commands.import_members import ImportMembersCommand


def import_members(request):
    context = {}

    if request.method == 'POST':
        form = ImportMembersForm(request.POST, request.FILES)
        if form.is_valid():
            success, import_log = ImportMembersCommand.import_members_file(request.FILES['file'])
            context['success'] = success
            context['import_log'] = import_log
    else:
        form = ImportMembersForm()

    context['form'] = form
    return render(request, 'import_members.html', context)
