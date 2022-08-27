from django.urls import path
from .views import performancetech_main_view, performancetech_load_view, getFileInfoPost, \
    deleteFilePost, chooseFilePost, selectedFilesPost, login_view, logout_view, create_performance_view, \
        show_presentation_view, deletePresentationPost, cancelSelectingFilesPost, history_view


urlpatterns = [
    path('performancetech/', performancetech_main_view),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('performancetech/load', performancetech_load_view),
    path('performancetech/file-info', getFileInfoPost, name='file-info'),
    path('performancetech/delete-file', deleteFilePost, name='delete-file'),
    path('performancetech/choose-file', chooseFilePost, name='choose-file'),
    path('performancetech/cancel-selecting-files', cancelSelectingFilesPost, name='cancel-selecting'),
    path('performancetech/selected-files', selectedFilesPost, name='selected-files'),
    path('performancetech/create-performance', create_performance_view),
    path('performancetech/<id>/show', show_presentation_view),
    path('performancetech/delete-presentation', deletePresentationPost, name='delete-presentation'),
    path('performancetech/history', history_view, name='history')
]