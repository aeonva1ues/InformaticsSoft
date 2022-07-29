from django.urls import path
from .views import py_compiler_view, user_inputs, contacts_page, manual_page


urlpatterns = [
    path('compiler/', py_compiler_view),
    path('compiler/input', user_inputs),
    path('contacts/', contacts_page),
    path('manual/', manual_page)
]