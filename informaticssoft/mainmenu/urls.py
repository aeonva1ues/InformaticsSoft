from django.urls import path
from .views import mainmenu_view


urlpatterns = [
    path('', mainmenu_view)
]