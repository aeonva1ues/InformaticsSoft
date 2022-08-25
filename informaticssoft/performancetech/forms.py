from django import forms

class UploadFileForm(forms.Form):
    sectionName = forms.CharField(max_length=50)
    fileName = forms.FileField()


class LoginUser(forms.Form):
    username = forms.CharField(max_length=255)
    password = forms.CharField(max_length=255)


class CreateWebPresentation(forms.Form):
    performanceName = forms.CharField(max_length=255)