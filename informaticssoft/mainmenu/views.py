from django.shortcuts import render

def mainmenu_view(request):
    return render(request, template_name='start_menu.html')
