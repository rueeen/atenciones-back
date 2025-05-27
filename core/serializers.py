from rest_framework import serializers
from .models import Usuario, Estudiante, Atencion, CategoriaAtencion, EstadoAtencion, DocumentoAdjunto, HistorialCambios, Area, Carrera


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'first_name',
                  'last_name', 'email', 'perfil', 'area']


class EstudianteSerializer(serializers.ModelSerializer):
    carrera = serializers.StringRelatedField()  # o CarreraSerializer() si quieres más detalle

    class Meta:
        model = Estudiante
        fields = ['id', 'rut', 'nombre', 'correo', 'carrera']
        
class EstudianteCreateUpdateSerializer(serializers.ModelSerializer):
    carrera = serializers.PrimaryKeyRelatedField(queryset=Carrera.objects.all())

    class Meta:
        model = Estudiante
        fields = ['id', 'rut', 'nombre', 'correo', 'carrera']

class CategoriaAtencionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaAtencion
        fields = '__all__'


class EstadoAtencionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoAtencion
        fields = '__all__'


class DocumentoAdjuntoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentoAdjunto
        fields = '__all__'


class HistorialCambiosSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialCambios
        fields = '__all__'


class AtencionSerializer(serializers.ModelSerializer):
    documentos = DocumentoAdjuntoSerializer(many=True, read_only=True)
    historial = HistorialCambiosSerializer(many=True, read_only=True)

    class Meta:
        model = Atencion
        fields = '__all__'


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'


class CarreraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrera
        fields = ['id', 'nombre']
