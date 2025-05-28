from rest_framework import serializers
from .models import Usuario, Estudiante, Atencion, CategoriaAtencion, EstadoAtencion, DocumentoAdjunto, HistorialCambios, Area, Carrera


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'first_name',
                  'last_name', 'email', 'perfil', 'area']


class EstudianteSerializer(serializers.ModelSerializer):
    # o CarreraSerializer() si quieres más detalle
    carrera = serializers.StringRelatedField()

    class Meta:
        model = Estudiante
        fields = ['id', 'rut', 'nombre', 'correo', 'carrera']


class EstudianteCreateUpdateSerializer(serializers.ModelSerializer):
    carrera = serializers.PrimaryKeyRelatedField(
        queryset=Carrera.objects.all())

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


# core/serializers.py
class HistorialCambiosSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.SerializerMethodField()

    class Meta:
        model = HistorialCambios
        fields = ['id', 'fecha', 'descripcion', 'usuario_nombre']

    def get_usuario_nombre(self, obj):
        if obj.usuario:
            return f"{obj.usuario.first_name} {obj.usuario.last_name}".strip() or obj.usuario.username
        return None


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


class AtencionTrasladoSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all())

    class Meta:
        model = Atencion
        fields = ['usuario']


class CarreraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrera
        fields = ['id', 'nombre']
