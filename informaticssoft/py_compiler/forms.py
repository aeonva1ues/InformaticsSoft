from django import forms


class CheckCode(forms.Form):
    code_editor = forms.CharField()


