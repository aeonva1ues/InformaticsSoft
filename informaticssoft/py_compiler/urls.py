from django.urls import path
from .views import py_compiler_view, user_inputs, contacts_page, manual_page


urlpatterns = [
    path('code-editor/', py_compiler_view),
    path('code-editor/input', user_inputs),
    path('contacts/', contacts_page),
    path('manual/', manual_page)
]