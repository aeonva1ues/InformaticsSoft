from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings

def mainmenu_view(request):
    return render(request, template_name='start_menu.html')


def FAQ_terms_view(request):
    # Словарь проекта
    with open(f'{settings.BASE_DIR}\\media\\txt_content\\project_terms.txt', 'r', encoding='utf-8') as file:
        content = file.read().split('\n')
        content = '<br>'.join(content)
    return HttpResponse('<title>Словарь проекта</title> <b>Словарь терминов проекта:</b><br><br><br>{}'.format(content))