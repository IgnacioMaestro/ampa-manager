from django import forms
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.camps.camps_edition import CampsEdition


class ImportCampsForm(forms.Form):
    camps_edition = forms.ModelChoiceField(
        queryset=CampsEdition.objects.order_by('-id'), label=_('Camp edition to import to'))
    file = forms.FileField()
    simulation = forms.BooleanField(
        required=False, label=_('SIMULATION: Only list the changes without making any'),
        initial=True)