from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'rut', 'email', 'career', 'schedule', 'created_at')
    search_fields = ('full_name', 'rut', 'email')
    list_filter = ('career', 'schedule')
