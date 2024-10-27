from django import forms
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.camps.camps_edition import CampsEdition
from ampa_manager.activity.models.custody.custody_edition import CustodyEdition


class ImportMembersForm(forms.Form):
    file = forms.FileField()
    simulation = forms.BooleanField(
        required=False, label=_('TEST THE IMPORT (it does not make any changes)'),
        initial=True)


class ImportAfterSchoolsRegistrationsForm(forms.Form):
    file = forms.FileField()


class ImportAfterSchoolsActivitiesForm(forms.Form):
    file = forms.FileField()


class ImportCustodyForm(forms.Form):
    custody_edition = forms.ModelChoiceField(
        queryset=CustodyEdition.objects.of_current_academic_course().order_by('-id'),
        label=_('Custody edition to import to'))
    file = forms.FileField()
    simulation = forms.BooleanField(
        required=False, label=_('TEST THE IMPORT (it does not make any changes)'),
        initial=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['custody_edition'].queryset = CustodyEdition.objects.of_current_academic_course().order_by('-id')


class ImportCampsForm(forms.Form):
    camps_edition = forms.ModelChoiceField(
        queryset=CampsEdition.objects.order_by('-id'), label=_('Camp edition to import to'))
    file = forms.FileField()
    simulation = forms.BooleanField(
        required=False, label=_('SIMULATION: Only list the changes without making any'),
        initial=True)


class CheckMembersForm(forms.Form):
    file = forms.FileField()


class ImportFamilyEmailForm(forms.Form):
    file = forms.FileField()


class CheckFamilyEmailForm(forms.Form):
    emails = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'placeholder': _('Write emails separated by comma or each one in one line'),
                'style': 'width: 700px; height: 200px;'
            }), label='Correos electrónicos')
