from django.http import FileResponse
from django.shortcuts import render
from django.views import View

from ampa_manager.forms import CheckMembersForm
from ampa_manager.views.membership_excel_checker import MembershipExcelChecker


class MemberChecker(View):
    @classmethod
    def get(cls, request):
        context = {
            'form': CheckMembersForm(),
            'form_action': '/ampa/members/check/',
            'excel_template_file_name': 'templates/plantilla_consultar_socios.xls'
        }
        return render(request, 'check_members.html', context)

    @classmethod
    def post(cls, request):
        return FileResponse(cls.obtain_checked_file(request.FILES['file']))

    @classmethod
    def obtain_checked_file(cls, request_file):
        checker = MembershipExcelChecker(request_file)
        checked_file = checker.get_file()
        return checked_file
