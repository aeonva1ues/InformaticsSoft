from django.urls import path

from performancetech.views import (
    all_notes_view, cancelSelectingFilesPost, chooseFilePost,
    create_performance_view, deleteFilePost,
    deletePresentationPost, getFileInfoPost, history_view,
    login_view, logout_view, notes_page_view,
    performancetech_load_view, performancetech_main_view,
    selectedFilesPost, show_presentation_view
)

urlpatterns = [
    path('performancetech/', performancetech_main_view),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('performancetech/load', performancetech_load_view),
    path('performancetech/file-info', getFileInfoPost, name='file-info'),
    path('performancetech/delete-file', deleteFilePost, name='delete-file'),
    path('performancetech/choose-file', chooseFilePost, name='choose-file'),
    path(
        'performancetech/cancel-selecting-files',
        cancelSelectingFilesPost,
        name='cancel-selecting'
        ),
    path(
        'performancetech/selected-files',
        selectedFilesPost,
        name='selected-files'),
    path('performancetech/create-performance', create_performance_view),
    path('performancetech/<id>/show', show_presentation_view),
    path(
        'performancetech/delete-presentation',
        deletePresentationPost,
        name='delete-presentation'
        ),
    path('performancetech/history', history_view, name='history'),
    path('performancetech/notes', all_notes_view, name='notes'),
    path(
        'performancetech/notes/<notes_id>',
        notes_page_view, name='notes_page'
        ),
]
