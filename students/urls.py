from django.urls import path
from .views import StudentCreateView, StudentListView, StudentUpdateView, StudentModalCreateView


app_name = 'students'

urlpatterns = [
    path('', StudentListView.as_view(), name='list'),
    path('nuevo/', StudentCreateView.as_view(), name='create'),
    path('modal/create/', StudentModalCreateView.as_view(), name='modal_create'),
    path('<int:pk>/edit/', StudentUpdateView.as_view(), name='update'),
]
