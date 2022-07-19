from django.shortcuts import render
from .forms import CheckCode


def py_compiler_view(request):
    if request.method == 'POST':
        form = CheckCode(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code_editor']
            try:
                result = exec(code)
            except Exception as code_error:
                result = code_error
    return render(request, 'py_compiler/compiler_page.html')
