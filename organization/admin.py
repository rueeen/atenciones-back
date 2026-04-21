from django.contrib import admin
from .models import AcademicArea, Area, Career


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(AcademicArea)
class AcademicAreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'area')
    search_fields = ('name', 'area__name')
    list_filter = ('area',)
    ordering = ('name',)


@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'academic_area')
    search_fields = ('name', 'academic_area__name')
    list_filter = ('academic_area',)
    ordering = ('name',)
