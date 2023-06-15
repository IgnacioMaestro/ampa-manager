from django.http import FileResponse
from django.shortcuts import render

from ampa_manager.forms import CheckMembersForm
from ampa_manager.views.membership_excel_checker import MembershipExcelChecker


def check_members(request):
    if request.method == 'POST':
        return FileResponse(obtain_checked_file(request.FILES['file']))

    context = {
        'form': CheckMembersForm(),
        'form_action': '/ampa/members/check/',
        'excel_template_file_name': 'templates/plantilla_consultar_socios.xls'
    }
    return render(request, 'check_members.html', context)


def obtain_checked_file(request_file):
    checker = MembershipExcelChecker(request_file)
    checked_file = checker.get_file()
    return checked_file
