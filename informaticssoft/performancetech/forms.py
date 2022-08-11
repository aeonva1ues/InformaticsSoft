from django import forms

class UploadFileForm(forms.Form):
    sectionName = forms.CharField(max_length=50)
    fileName = forms.FileField()