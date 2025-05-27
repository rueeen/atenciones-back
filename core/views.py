from rest_framework import generics, status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Estudiante, Atencion, Usuario, Carrera, CategoriaAtencion, EstadoAtencion
from .serializers import (
    EstudianteSerializer,
    EstudianteCreateUpdateSerializer,
    AtencionSerializer,
    UsuarioSerializer,
    CarreraSerializer,
    CategoriaAtencionSerializer,
    EstadoAtencionSerializer
)

# --- ESTUDIANTE ---


""" class EstudianteListCreate(APIView):
    def get(self, request):
        estudiantes = Estudiante.objects.all()
        serializer = EstudianteSerializer(estudiantes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EstudianteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) """


class EstudianteListCreate(generics.ListCreateAPIView):
    queryset = Estudiante.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EstudianteCreateUpdateSerializer
        return EstudianteSerializer


class EstudianteDetail(APIView):
    def get(self, request, pk):
        estudiante = get_object_or_404(Estudiante, pk=pk)
        serializer = EstudianteSerializer(estudiante)
        return Response(serializer.data)

    def put(self, request, pk):
        estudiante = get_object_or_404(Estudiante, pk=pk)
        serializer = EstudianteSerializer(estudiante, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        estudiante = get_object_or_404(Estudiante, pk=pk)
        estudiante.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# --- ATENCIÓN ---


class AtencionListCreate(APIView):
    def get(self, request):
        atenciones = Atencion.objects.all()
        serializer = AtencionSerializer(atenciones, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AtencionSerializer(data=request.data)
        if serializer.is_valid():
            atencion = serializer.save()
            return Response(AtencionSerializer(atencion).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AtencionDetail(APIView):
    def get(self, request, pk):
        atencion = get_object_or_404(Atencion, pk=pk)
        serializer = AtencionSerializer(atencion)
        return Response(serializer.data)

    def put(self, request, pk):
        atencion = get_object_or_404(Atencion, pk=pk)
        serializer = AtencionSerializer(atencion, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        atencion = get_object_or_404(Atencion, pk=pk)
        atencion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UsuarioActual(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "perfil": user.perfil,
            "is_superuser": user.is_superuser,
        })


class UsuarioCreateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            usuario = Usuario.objects.create_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                first_name=serializer.validated_data.get('first_name', ''),
                last_name=serializer.validated_data.get('last_name', ''),
                password=request.data['password'],
                perfil=serializer.validated_data['perfil']
            )
            return Response(UsuarioSerializer(usuario).data, status=201)
        return Response(serializer.errors, status=400)


class UsuarioCreateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            usuario = Usuario.objects.create_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                first_name=serializer.validated_data.get('first_name', ''),
                last_name=serializer.validated_data.get('last_name', ''),
                password=request.data['password'],
                perfil=serializer.validated_data['perfil']
            )
            return Response(UsuarioSerializer(usuario).data, status=201)
        return Response(serializer.errors, status=400)


class CategoriaAtencionListView(ListAPIView):
    queryset = CategoriaAtencion.objects.all()
    serializer_class = CategoriaAtencionSerializer
    permission_classes = [IsAuthenticated]


class EstadoAtencionListView(ListAPIView):
    queryset = EstadoAtencion.objects.all()
    serializer_class = EstadoAtencionSerializer
    permission_classes = [IsAuthenticated]


class CarreraListView(ListAPIView):
    queryset = Carrera.objects.all()
    serializer_class = CarreraSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(nombre__icontains=search)
        return queryset
