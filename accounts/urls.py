from django.urls import path
from .views import UserCreateView

app_name = 'accounts'

urlpatterns = [
    path('users/new/', UserCreateView.as_view(), name='user-create'),
]
