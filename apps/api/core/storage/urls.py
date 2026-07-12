from django.urls import path

from storage.views import UploadUrlView, ConfirmUploadView, DownloadUrlView

urlpatterns = [
    path(
        'projects/<uuid:project_pk>/files/upload-url/',
        UploadUrlView.as_view(),
        name='file-upload-url',
    ),
    path('files/<uuid:file_id>/confirm/', ConfirmUploadView.as_view(), name='file-confirm'),
    path('files/<uuid:file_id>/download-url/', DownloadUrlView.as_view(), name='file-download-url'),
]
