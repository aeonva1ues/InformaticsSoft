from django.urls import path
from .views import performancetech_main_view, performancetech_load_view, getFileInfoPost, \
    deleteFilePost


urlpatterns = [
    path('performancetech/', performancetech_main_view),
    path('performancetech/load', performancetech_load_view),
    path('performancetech/file-info', getFileInfoPost, name='file-info'),
    path('performancetech/delete-file', deleteFilePost, name='delete-file')
]