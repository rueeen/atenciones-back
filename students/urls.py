from django.urls import path
from .views import StudentCreateView, StudentListView, StudentUpdateView

app_name = 'students'

urlpatterns = [
    path('', StudentListView.as_view(), name='list'),
    path('new/', StudentCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', StudentUpdateView.as_view(), name='update'),
]
