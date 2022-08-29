from django.urls import path
from .views import mainmenu_view, FAQ_terms_view


urlpatterns = [
    path('', mainmenu_view),
    path('FAQ/terms', FAQ_terms_view)
]