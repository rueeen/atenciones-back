from django.urls import path

from psychopedagogy.views import (
    PsychopedagogyAttachmentCreateView,
    PsychopedagogyLogEntryCreateView,
    PsychopedagogyRecordCreateView,
    PsychopedagogyRecordDetailView,
    PsychopedagogyRecordListView,
)

app_name = 'psychopedagogy'

urlpatterns = [
    path('', PsychopedagogyRecordListView.as_view(), name='list'),
    path('nuevo/', PsychopedagogyRecordCreateView.as_view(), name='create'),
    path('<int:pk>/', PsychopedagogyRecordDetailView.as_view(), name='detail'),
    path('<int:pk>/bitacora/', PsychopedagogyLogEntryCreateView.as_view(), name='add-log'),
    path('<int:pk>/adjunto/', PsychopedagogyAttachmentCreateView.as_view(), name='add-attachment'),
]
