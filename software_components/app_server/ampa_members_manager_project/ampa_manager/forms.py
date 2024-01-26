from django import forms
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.camps.camps_edition import CampsEdition
from ampa_manager.activity.models.custody.custody_edition import CustodyEdition


class ImportMembersForm(forms.Form):
    file = forms.FileField()


class ImportAfterSchoolsRegistrationsForm(forms.Form):
    file = forms.FileField()


class ImportAfterSchoolsActivitiesForm(forms.Form):
    file = forms.FileField()


class ImportCustodyForm(forms.Form):
    custody_edition = forms.ModelChoiceField(
        queryset=CustodyEdition.objects.order_by('-id'),
        label=_('Custody edition to import to'))
    file = forms.FileField()


class ImportCampsForm(forms.Form):
    camps_edition = forms.ModelChoiceField(
        queryset=CampsEdition.objects.order_by('-id'), label=_('Camp edition to import to'))
    file = forms.FileField()


class CheckMembersForm(forms.Form):
    file = forms.FileField()
