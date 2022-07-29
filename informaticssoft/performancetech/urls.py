from django.urls import path
from .views import performancetech_main_view


urlpatterns = [
    path('performancetech/', performancetech_main_view)
]