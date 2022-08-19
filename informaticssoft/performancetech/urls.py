from django.urls import path
from .views import performancetech_main_view, performancetech_load_view, getFileInfoPost, \
    deleteFilePost, chooseFilePost, selectedFilesPost, login_view, logout_view


urlpatterns = [
    path('performancetech/', performancetech_main_view),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('performancetech/load', performancetech_load_view),
    path('performancetech/file-info', getFileInfoPost, name='file-info'),
    path('performancetech/delete-file', deleteFilePost, name='delete-file'),
    path('performancetech/choose-file', chooseFilePost, name='choose-file'),
    path('performancetech/selected-files', selectedFilesPost, name='selected-files')
]