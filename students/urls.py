from django.urls import path
from .views import (
    StudentCreateView,
    StudentListView,
    StudentLookupByRutView,
    StudentModalCreateView,
    StudentUpdateView,
    CareersByAcademicAreaView,
)


app_name = 'students'

urlpatterns = [
    path('', StudentListView.as_view(), name='list'),
    path('ajax/by-rut/', StudentLookupByRutView.as_view(), name='by_rut'),
    path('modal/create/', StudentModalCreateView.as_view(), name='modal_create'),
    path('<int:pk>/edit/', StudentUpdateView.as_view(), name='update'),
    path('nuevo/', StudentCreateView.as_view(), name='create'),
    path(
        'ajax/careers-by-academic-area/',
        CareersByAcademicAreaView.as_view(),
        name='careers_by_academic_area'
    ),
]
