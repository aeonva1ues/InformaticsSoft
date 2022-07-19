from django.urls import path
from .views import py_compiler_view


urlpatterns = [
    path('compiler/', py_compiler_view)
]