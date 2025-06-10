from django.contrib import admin
from core.models import Usuario, Carrera, Estudiante, Atencion, CategoriaAtencion, EstadoAtencion, DocumentoAdjunto, HistorialCambios, Area

# Register your models here.
admin.site.register(Usuario)
admin.site.register(Carrera)
admin.site.register(Estudiante)
admin.site.register(Atencion)
admin.site.register(CategoriaAtencion)
admin.site.register(EstadoAtencion)
admin.site.register(DocumentoAdjunto)
admin.site.register(HistorialCambios)
admin.site.register(Area)