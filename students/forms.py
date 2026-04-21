from django import forms
from students.models import Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['full_name', 'rut', 'email', 'phone', 'career', 'schedule', 'observations']
        labels = {
            'full_name': 'Nombre completo',
            'rut': 'RUT',
            'email': 'Correo electrónico',
            'phone': 'Teléfono',
            'career': 'Carrera',
            'schedule': 'Jornada',
            'observations': 'Observaciones',
        }
