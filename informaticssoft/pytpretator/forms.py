from django import forms


class CheckCode(forms.Form):
    code_editor = forms.CharField()


class TypeUserInput(forms.Form):
    template_name = 'pytpretator/input_fields.html'
