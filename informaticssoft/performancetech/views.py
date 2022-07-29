from django.shortcuts import render


# Performancetech - софт для удобного длительного хранения файлов и данных для выступлений.
# Доступ к странице имеют только суперпользователи. Суперпользователь может смотреть, скачивать и загружать файлы.

def performancetech_main_view(request):
    return render(request, 'performancetech/mainpage.html')
