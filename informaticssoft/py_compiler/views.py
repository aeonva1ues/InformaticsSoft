import io
import queue
import sys
import threading
import time

from django.http import HttpResponseRedirect
from django.shortcuts import render
from py_compiler.models import Manual_Section

from .forms import CheckCode, TypeUserInput


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self,  *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


def run_code(__code):
    __with_error = False
    __codeOut = io.StringIO()
    sys.stdout = __codeOut
    try:
        exec(f'''{__code}
        \n__ALLVARIABLES_STR = ''
        \n__ALLVARIABLES_U = dir()
        \nfor variable in __ALLVARIABLES_U:
        \n\tif variable == '__code' or \
        \t\t\tvariable == '__codeOut' or \
        \t\t\tvariable == '__with_error' or \
        \t\t\tvariable == '__ALLVARIABLES_STR':
        \n\t\tpass
        \n\telse:
        \n\t\t__stypes = str(type(locals()[variable]))
        \n\t\t__stypes = __stypes.lstrip("<class '").rstrip("'>")
        \n\t\t__svars = str(locals()[variable])
        \n\t\t__ALLVARIABLES_STR += variable + '=' + __stypes
        \n\t\t__ALLVARIABLES_STR += '=' + __svars + 'SEPSEPsepSeP'
        \nprint(__ALLVARIABLES_STR)
        ''')
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        result = __codeOut.getvalue()
    except Exception as code_error:
        __with_error = True
        result = code_error
    finally:
        sys.stdout.close()
        __codeOut.close()
        return (result, __with_error)


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
            code = request.POST.get('code_editor')
            code_lines = code.split('\n')
            request.session['code_lines'] = code_lines
            # Опасные импорты - Все модули, кроме Math, Random, Datetime
            danger_imports = False
            # Попытка взаимодействия с файлами
            danger_using_files = False
            # Тяжелые функции, не выполняющиеся через exec()
            heavy_functions = False
            lines_with_input = []
            line_counter = 0
            for code_line in code_lines:
                if 'import' in code_line:
                    if 'math' in code_line or 'random' in code_line \
                            or 'datetime' in code_line \
                            or 'this' in code_line:
                        '''
                        === Разрешенные модули ===
                        '''
                        pass
                    else:
                        danger_imports = True
                if 'file' in code_line or '.read()' in code_line \
                        or '.write()' in code_line:
                    danger_using_files = True
                if 'help()' in code_line:
                    heavy_functions = True
                if 'input(' in code_line and \
                        '# введено пользователем через input()' \
                        not in code_line and \
                        (
                            '# Вы не указали, '
                            'куда сохранять данные, введенные через input()'
                            ) not in code_line:
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
            if not danger_imports \
                    and not danger_using_files \
                    and not heavy_functions:
                que = queue.Queue()
                thr = StoppableThread(
                    target=lambda q,
                    arg: q.put(run_code(arg)),
                    args=(que, code))
                thr.start()
                for t in range(12):
                    if not que.empty():
                        # Результат работы кода есть
                        thr_return = que.get()
                        result = thr_return[0]
                        with_error = thr_return[1]
                        thr.stop()
                        # sys.stdout = ''   # очистка ввода
                        break
                    if t == 2:
                        result = (
                            'RuntimeError: Длительность выполнения программы '
                            'превышает лимит. '
                            'Возможно, используется бесконечный цикл'
                        )
                        with_error = True
                        thr.stop()
                        # sys.stdout = ''   # очистка ввода
                        break
                    time.sleep(0.25)
            else:
                with_error = True
                result = ''
                if danger_imports:
                    result = result + 'Вы использовали запрещенные импорты!\n'
                if danger_using_files:
                    result = result + \
                        'Похоже, вы пытались взаимодействовать с файлами!\n'
                if heavy_functions:
                    result = result + \
                        (
                            'Вы использовали функцию, '
                            'внесенную в список исключений!\n'
                        )
            if not with_error:
                finish_variables_str = result.split('\n')[-2]
                variables_with_value = finish_variables_str.split(
                    'SEPSEPsepSeP')  # сепаратор
                finish_variables = []
                for var_val in variables_with_value:
                    if var_val:
                        var_val_line = var_val.split('=')
                        variable = var_val_line[0].strip()
                        var_format = var_val_line[1].strip()
                        value = var_val_line[2].strip()
                        finish_variables.append(
                            {
                                'variable': variable,
                                'format': var_format
                                .replace('ist', 'list')
                                .replace('tr', 'str'),
                                'value': value
                            }
                        )
                context['finish_variables'] = finish_variables
                result = result.split('\n')[:-2]
            context['last_code'] = code
            context['with_error'] = with_error
            context['code_result'] = result

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
                part_with_func = code_line[1].strip()
                variable = code_line[0].strip()
                value = user_input_results[
                    f'input_{str(input_field["line_index"])}'
                    ]
                multi_input = False

                if len(variable) > 2 and ',' in variable \
                        and '.split(' in part_with_func:
                    splited_by = part_with_func.split('.split(')[1]
                    splited_by = splited_by.split(')')[0].split('.')[0]
                    if not splited_by \
                            or splited_by == "''" \
                            or splited_by == '""':
                        splited_by = ' '
                    else:
                        splited_by = splited_by[1:-1]
                    args = value.split(splited_by)
                    new_value = ''
                    arg_index = 0
                    args_count = len(args)
                    multi_input = True
                    for arg in args:
                        if arg_index != args_count-1:
                            new_value = new_value + "'{}', ".format(
                                arg.strip("'"))
                        else:
                            # Устранение лишней запятой
                            new_value = new_value + "'{}'".format(
                                arg.strip("'"))
                        arg_index += 1
                    value = f'({new_value})'
                lost_bracket = False
                if part_with_func[-1] != ')':
                    # утерянная закрывающая скобка в Input()
                    lost_bracket = True
                lost_split_in_multi_input = False
                if 'map(' in part_with_func:
                    if multi_input:
                        map_args_line = part_with_func.split('map(')[1][:-1]
                        format_arg = map_args_line.split(',')[0].strip()
                        if format_arg == 'int' \
                                or format_arg == 'str' \
                                or format_arg == 'bool' \
                                or format_arg == 'float':
                            formated_value = value.split("'")[1:-1]
                            for index in range(len(formated_value)):
                                if formated_value[index].strip() != ",":
                                    formated_value[index] = (
                                        f'{format_arg}'
                                        f'("{formated_value[index]}")'
                                    )
                            value = f'({"".join(formated_value)})'
                    else:
                        lost_split_in_multi_input = True
                else:
                    if 'int(' in part_with_func:
                        value = f'int("{value}")'
                    elif 'float(' in part_with_func:
                        value = f'float("{value}")'
                    elif 'bool(' in part_with_func:
                        value = f'bool("{value}")'
                    else:
                        if not multi_input:
                            value = f'"{value}"'

            line_index = input_field['line_index']
            if not variable:
                code[line_index] = (
                    '# Вы не указали, куда сохранять данные, '
                    'введенные через input()'
                    )
            elif lost_bracket:
                code[line_index] = (
                    '# Ошибка синтаксиса в строке с input(). '
                    'Скобка не закрыта'
                    )
            elif lost_split_in_multi_input:
                code[line_index] = (
                    '# Ошибка множественного ввода. '
                    'Необходим split() введенных данных'
                )
            else:
                tabs = ''
                this_line_in_code = code[line_index]
                if '\t' in this_line_in_code:
                    for symbol in this_line_in_code:
                        if symbol == '\t':
                            tabs = tabs + symbol
                code[line_index] = (
                    f'{tabs}{variable} = {value}'
                    ' # введено пользователем через input()'
                )
            counter += 1
        request.session.pop('inputs_lines')
        request.session['new_code'] = code
        return HttpResponseRedirect('/code-editor/')

    if 'inputs_lines' in request.session:
        input_fields = request.session['inputs_lines']
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
                # True если цикл вошел в комментарий в input( X X )
                flag = False
                comment_text = ''
                part_with_input = part_with_func.split('input(')[1]\
                                                .split(')')[0]
                for letter in part_with_input:
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
            return HttpResponseRedirect('/code-editor/', status=301)
    else:
        return HttpResponseRedirect('/code-editor/', status=301)


def contacts_page(request):
    return render(request, 'py_compiler/contacts.html')


def manual_page(request):
    context = {}
    sections = Manual_Section.objects.all()
    context_sections = []
    for section in sections:
        info_blocks = section.infoblock.all()
        context_sections.append(
            {
                'section_name': section.name,
                'info_blocks': info_blocks
            }
        )
    context['sections'] = context_sections
    return render(request, 'py_compiler/manual.html', context)
