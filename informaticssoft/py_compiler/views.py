import sys
import io
from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import CreateView

from .forms import CheckCode, TypeUserInput


def py_compiler_view(request):
    context = {}
    if 'new_code' in request.session:
        new_code = request.session['new_code']
        request.session.pop('new_code')
        code = '\n'.join(new_code)
        context = {'last_code': code}
    if request.method == 'POST':
        form = CheckCode(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code_editor']
            code_lines = code.split('\n')
            request.session['code_lines'] = code_lines
            # Опасные импорты - Все модули, кроме Math, Random, Datetime
            danger_imports = False
            # Попытка взаимодействия с файлами
            danger_using_files = False
            # Тяжелые функции, не выполняющиеся через exec()
            heavy_functions = False
            # Бесконечный цикл
            infinity_loop = False
            # input() строки в коде
            lines_with_input = []
            line_counter = 0
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
                if 'while' in code_line:
                    infinity_loop = True
                if 'input(' in code_line and '# введено пользователем через input()' not in code_line and \
                        '# Вы не указали, куда сохранять данные, введенные через input()' not in code_line:
                    lines_with_input.append(
                        {
                            'code_line': code_line,
                            'line_index': line_counter
                        }
                    )
                line_counter += 1
            if len(lines_with_input) > 0 and 'new_code' not in request.session:
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
                    result = result + 'Использование цикла while в данном компиляторе запрещено. ' \
                                      'Практика по данному циклу в разделе "Примеры"'

            context = {
                'last_code': code,
                'with_error': with_error,
                'code_result': result
            }
    return render(request, 'py_compiler/compiler_page.html', context=context)


def user_inputs(request):
    if request.method == 'POST':
        form = TypeUserInput(request.POST)
        input_fields = request.session['inputs_lines']
        user_input_results = form.data
        code = request.session['code_lines']
        counter = 0
        for input_field in input_fields:
            # Обработка введенных полей
            code_line = input_field['code_line'].split('=')
            if len(code_line) < 2:
                variable = None
            else:
                variable = code_line[0].strip()
                value = user_input_results[f'input_{str(input_field["line_index"])}']
                part_with_func = code_line[1].strip()
                if 'int(' in part_with_func:
                    value = f'int("{value}")'
                elif 'float(' in part_with_func:
                    value = f'float("{value}")'
                elif 'bool(' in part_with_func:
                    value = f'bool("{value}")'
                else:
                    value = f'"{value}"'
            line_index = input_field['line_index']
            if not variable:
                code[line_index] = f'# Вы не указали, куда сохранять данные, введенные через input()'
            else:
                tabs = ''
                this_line_in_code = code[line_index]
                if '\t' in this_line_in_code:
                    for symbol in this_line_in_code:
                        if symbol == '\t':
                            tabs = tabs + symbol
                code[line_index] = f'{tabs}{variable} = {value} # введено пользователем через input()'
            counter += 1
        request.session['new_code'] = code
        return HttpResponseRedirect('/compiler/')

    input_fields = request.session['inputs_lines']  # {'code_line', 'line_index'}
    fields_data = []
    if len(input_fields) > 0:
        for input_field in input_fields:
            code_line = input_field['code_line']
            input_field_data = code_line.split('=')

            if len(input_field_data) == 1:
                variable = 'input()'
                index = 0
            else:
                variable = input_field_data[0].strip()
                index = 1
            part_with_func = input_field_data[index].strip()
            flag = False  # True если цикл вошел в комментарий в input( X X )
            comment_text = ''
            for letter in part_with_func:
                if letter == '"' or letter == "'":
                    if flag:
                        # Попалась вторая кавычка
                        break
                    flag = True
                elif flag:
                    comment_text = comment_text + letter
            fields_data.append(
                {
                    'variable': variable,
                    'index': input_field['line_index'],
                    'comment': comment_text
                }
            )
        context = {'input_fields': fields_data}
        return render(request, 'py_compiler/input_fields.html', context)
    else:
        return HttpResponseRedirect('/compiler/')


def contacts_page(request):
    return render(request, 'py_compiler/contacts.html')


def manual_page(request):
    return render(request, 'py_compiler/manual.html')
