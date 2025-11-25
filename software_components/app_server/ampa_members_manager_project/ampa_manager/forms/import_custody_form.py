from django import forms
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition


class ImportCustodyForm(forms.Form):
    custody_edition = forms.ModelChoiceField(
        queryset=CustodyEdition.objects.order_by('-id'),
        label=_('Custody edition to import to'))
    file = forms.FileField()
    simulation = forms.BooleanField(
        required=False, label=_('TEST THE IMPORT (it does not make any changes)'),
        initial=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['custody_edition'].queryset = CustodyEdition.objects.of_current_academic_course().order_by('-id')
