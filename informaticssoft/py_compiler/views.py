import sys
import io
from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import CreateView

from .forms import CheckCode, TypeUserInput


def py_compiler_view(request):
    context = {
        'last_code': request.session['code']
    }
    if request.method == 'POST' or request.session['input-result'] == 'Without Changes':
        form = CheckCode(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code_editor']
            request.session['code'] = code
            code_lines = code.split('\n')
            # Опасные импорты - Все импорты, кроме модуля Math, Random, Datetime
            danger_imports = False
            # Попытка взаимодействия с файлами
            danger_using_files = False
            # Тяжелые функции, не выполняющиеся через exec()
            heavy_functions = False
            # Бесконечный цикл
            infinity_loop = False
            # input() строки в коде
            lines_with_input = []
            for code_line in code_lines:
                if 'import' in code_line:
                    if 'math' in code_line or 'random' in code_line or 'datetime' in code_line \
                            or 'this' in code_line:
                        '''
                        === Разрешенные модули ===
                        '''
                        pass
                    else:
                        danger_imports = True
                if '.read()' in code_line or '.write()' in code_line:
                    danger_using_files = True
                if 'help()' in code_line:
                    heavy_functions = True
                if 'while True' in code_line:
                    infinity_loop = True
                if 'input()' in code_line:
                    lines_with_input.append(code_line)
            if len(lines_with_input) > 0 and not request.session['input-result']:
                request.session['inputs_lines'] = lines_with_input
                return HttpResponseRedirect('input')
            if not danger_imports and not danger_using_files and not heavy_functions and not infinity_loop:
                with_error = False
                codeOut = io.StringIO()
                sys.stdout = codeOut
                try:
                    exec(code)
                    sys.stdout = sys.__stdout__
                    sys.stderr = sys.__stderr__
                    result = codeOut.getvalue()
                except Exception as code_error:
                    with_error = True
                    result = code_error
                finally:
                    codeOut.close()
            else:
                with_error = True
                result = ''
                if danger_imports:
                    result = result + 'Вы использовали запрещенные импорты!\n'
                if danger_using_files:
                    result = result + 'Похоже, вы пытались взаимодействовать с файлами!\n'
                if heavy_functions:
                    result = result + 'Вы использовали функцию, внесенную в список исключений!\n'
                if infinity_loop:
                    result = result + 'Вы явно использовали бесконечный цикл. ' \
                                      'Конструкция while True не является хорошей идеей реализации.\n'

            context = {
                'last_code': request.session['code'],
                'with_error': with_error,
                'code_result': result
            }
    return render(request, 'py_compiler/compiler_page.html', context=context)


def user_inputs(request):
    input_fields = request.session['inputs_lines']
    fields_data = []
    if len(input_fields) > 0:
        for input_field in input_fields:
            if input_field.strip() == 'int(input())' or input_field.strip() == 'input()':
                request.session['input-result'] = 'Without changes'
                request.session['changed-code'] = request
                return HttpResponseRedirect('/compiler/')
            input_field_data = input_field.split('=')
            variable = input_field_data[0].strip()
            value = input_field_data[1].strip()
            if value[0:2] == 'int':
                input_type = 'int'
            else:
                input_type = 'str'
            comment_for_input = value.split('(')[1].replace(')', '')
            fields_data.append(
                {
                    'variable': variable,
                    'input_type': input_type,
                    'comment_for_input': comment_for_input
                }
            )
        context = {'input_fields': fields_data}
        return render(request, 'py_compiler/input_fields.html', context)
    else:
        return HttpResponseRedirect('/compiler/')
