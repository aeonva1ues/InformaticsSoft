from django.urls import path

from .views import (
    contacts_page, manual_page,
    py_compiler_view, user_inputs, examples_page,
    get_video
    )


app_name = 'pytpr'
urlpatterns = [
    path('code-editor/', py_compiler_view),
    path('code-editor/input/', user_inputs),
    path('contacts/', contacts_page),
    path('manual/', manual_page),
    path('examples/', examples_page),
    path('examples/get_video', get_video, name='get-video')
]
