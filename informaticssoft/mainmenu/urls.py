from django.urls import path

from .views import FAQ_view, mainmenu_view

urlpatterns = [
    path('', mainmenu_view),
    path('FAQ/<faq_type>/', FAQ_view)
]
