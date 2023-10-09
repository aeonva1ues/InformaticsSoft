from django.urls import path

from pytpretator.views import (
    contacts_page, manual_page,
    py_interpreter_view, user_inputs, examples_page,
    )


urlpatterns = [
    path('code-editor/', py_interpreter_view),
    path('code-editor/input/', user_inputs),
    path('contacts/', contacts_page),
    path('manual/', manual_page),
    path('examples/', examples_page),
]
