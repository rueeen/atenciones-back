from django.urls import path
from .views import (
    CarreraListView, CategoriaAtencionListView, EstadoAtencionListView, EstudianteListCreate,
    EstudianteDetail, AtencionListCreate, AtencionDetail, HistorialAtencionView, ListaUsuariosView, TrasladarAtencionView, UsuarioActual, UsuarioCreateView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Estudiantes
    path('estudiantes/', EstudianteListCreate.as_view(), name='estudiante-list'),
    path('estudiantes/<int:pk>/', EstudianteDetail.as_view(),
         name='estudiante-detail'),

    # Atenciones
    path('atenciones/', AtencionListCreate.as_view(), name='atencion-list'),
    path('atenciones/<int:pk>/', AtencionDetail.as_view(), name='atencion-detail'),
    path('categorias/', CategoriaAtencionListView.as_view(), name='categoria-list'),
    path('estados/', EstadoAtencionListView.as_view(), name='estado-list'),
    path('carreras/', CarreraListView.as_view(), name='carrera-list'),
    path('atenciones/<int:pk>/trasladar/',
         TrasladarAtencionView.as_view(), name='trasladar-atencion'),
    path('atenciones/<int:atencion_id>/historial/',
         HistorialAtencionView.as_view(), name='historial-atencion'),


    # JWT Authentication
    path('login/', TokenObtainPairView.as_view(),
         name='token_obtain_pair'),   # Login
    path('refresh/', TokenRefreshView.as_view(),
         name='token_refresh'),        # Refresh token

    # Usuarios
    path('me/', UsuarioActual.as_view(), name='usuario-actual'),
    path('usuarios/crear/', UsuarioCreateView.as_view(), name='usuario-crear'),
    path('usuarios/', ListaUsuariosView.as_view(), name='usuarios-list'),

]
