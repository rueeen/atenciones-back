from django.contrib import admin
from .models import AcademicArea, Area, Career


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_academic_direction')
    search_fields = ('name',)
    list_filter = ('is_academic_direction',)


@admin.register(AcademicArea)
class AcademicAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_area')
    search_fields = ('name',)
    list_filter = ('parent_area',)


@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display = ('name', 'academic_area')
    search_fields = ('name',)
    list_filter = ('academic_area',)
