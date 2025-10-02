from django import forms
from django.utils.translation import gettext_lazy as _


class GenerateMembersRemittanceForm(forms.Form):
    active_course_fee = forms.IntegerField(label=_('Members fee in active course'), required=True)
