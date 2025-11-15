from django import forms
from django.utils.translation import gettext_lazy as _


class ImportAfterSchoolsActivitiesForm(forms.Form):
    file = forms.FileField()
    simulation = forms.BooleanField(
        required=False, label=_('TEST THE IMPORT (it does not make any changes)'),
        initial=True)