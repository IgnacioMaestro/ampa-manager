from django import forms


class ImportMembersForm(forms.Form):
    file = forms.FileField()


class ImportAfterSchoolsForm(forms.Form):
    file = forms.FileField()


class ImportCustodyForm(forms.Form):
    file = forms.FileField()


class CheckMembersForm(forms.Form):
    file = forms.FileField()
