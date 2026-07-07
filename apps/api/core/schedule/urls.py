from django.urls import path

from schedule.views import MspImportPreviewView, MspImportStartView, MspImportStatusView

urlpatterns = [
    path('import/msp/preview/', MspImportPreviewView.as_view(), name='msp-import-preview'),
    path('import/msp/', MspImportStartView.as_view(), name='msp-import-start'),
    path('import/msp/status/<uuid:task_id>/', MspImportStatusView.as_view(), name='msp-import-status'),
]
