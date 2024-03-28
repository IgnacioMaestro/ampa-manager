from typing import List

from django.shortcuts import render
from django.views import View

from ampa_manager.family.models.family import Family
from ampa_manager.forms import CheckFamilyEmailForm


class CheckFamilyEmail(View):
    TEMPLATE = 'check_family_email.html'

    @classmethod
    def post(cls, request):
        form = CheckFamilyEmailForm(request.POST)
        emails_to_check = CheckFamilyEmail.extract_emails_to_check(form)
        emails_registered, emails_not_registered = CheckFamilyEmail.check_emails(emails_to_check)
        context = {
            'form': form,
            'emails_registered': emails_registered,
            'emails_not_registered': emails_not_registered,
        }
        return render(request, cls.TEMPLATE, context)

    @classmethod
    def extract_emails_to_check(cls, form) -> List[str]:
        emails_string = str(form.data['emails']).replace('\n', ',')
        return [email.strip() for email in emails_string.split(',')]

    @classmethod
    def get(cls, request):
        context = {'form': CheckFamilyEmailForm()}
        return render(request, cls.TEMPLATE, context)

    @classmethod
    def check_emails(cls, emails_to_check):
        emails_registered = []
        emails_not_registered = []

        for email in emails_to_check:
            families = Family.objects.with_this_email(email)
            if families.count() > 0:
                emails_registered.append([email, families.first().surnames])
            else:
                emails_not_registered.append(email)
        return emails_registered, emails_not_registered
