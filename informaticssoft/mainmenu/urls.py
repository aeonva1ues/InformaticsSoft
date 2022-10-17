from django.urls import path

from .views import FAQ_terms_view, mainmenu_view

urlpatterns = [
    path('', mainmenu_view),
    path('FAQ/terms', FAQ_terms_view)
]
