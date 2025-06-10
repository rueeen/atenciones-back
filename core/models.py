from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class Area(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Usuario(AbstractUser):
    PERFILES = [
        ('administrador', 'Administrador'),
        ('funcionario', 'Funcionario'),
    ]
    perfil = models.CharField(max_length=20, choices=PERFILES)
    area = models.ForeignKey(
        Area, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = _('usuario')
        verbose_name_plural = _('usuarios')


class Carrera(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Estudiante(models.Model):
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    carrera = models.ForeignKey(Carrera, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.nombre} ({self.rut})"


class CategoriaAtencion(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class EstadoAtencion(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre


class Atencion(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    funcionario = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True)
    categoria = models.ForeignKey(
        CategoriaAtencion, on_delete=models.SET_NULL, null=True)
    estado = models.ForeignKey(
        EstadoAtencion, on_delete=models.SET_NULL, null=True)
    motivo = models.TextField()
    observaciones = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Atención a {self.estudiante.nombre} - {self.fecha_creacion.date()}"


class DocumentoAdjunto(models.Model):
    atencion = models.ForeignKey(
        Atencion, on_delete=models.CASCADE, related_name='documentos')
    archivo = models.FileField(upload_to='documentos/')
    descripcion = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Documento para atención {self.atencion.id}"


class HistorialCambios(models.Model):
    atencion = models.ForeignKey(
        Atencion, on_delete=models.CASCADE, related_name='historial')
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField()

    def __str__(self):
        return f"Historial atención {self.atencion.id} por {self.usuario}"


class Derivacion(models.Model):
    atencion = models.ForeignKey(
        Atencion, on_delete=models.CASCADE, related_name='derivaciones')
    de_area = models.ForeignKey(
        Area, on_delete=models.SET_NULL, null=True, related_name='derivaciones_salientes')
    a_area = models.ForeignKey(
        Area, on_delete=models.SET_NULL, null=True, related_name='derivaciones_entrantes')
    usuario_deriva = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, related_name='derivaciones_realizadas')
    fecha = models.DateTimeField(auto_now_add=True)
    motivo = models.TextField()

    def __str__(self):
        return f"Derivación {self.atencion.id} de {self.de_area} a {self.a_area}"
