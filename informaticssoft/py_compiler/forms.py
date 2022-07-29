from django import forms


class CheckCode(forms.Form):
    code_editor = forms.CharField()


class TypeUserInput(forms.Form):
    template_name = 'py_compiler/input_fields.html'
