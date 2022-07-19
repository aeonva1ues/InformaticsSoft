from django.urls import path
from .views import py_compiler_view, user_inputs


urlpatterns = [
    path('compiler/', py_compiler_view),
    path('compiler/input', user_inputs)
]