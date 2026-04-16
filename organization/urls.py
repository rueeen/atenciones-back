from django.urls import path
from .views import AreaListView, CareerListView

app_name = 'organization'
urlpatterns = [
    path('areas/', AreaListView.as_view(), name='areas'),
    path('careers/', CareerListView.as_view(), name='careers'),
]
