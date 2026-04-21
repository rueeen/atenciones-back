from django import forms
from students.models import Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['full_name', 'rut', 'email', 'phone',
                  'career', 'schedule', 'observations']
        labels = {
            'full_name': 'Nombre completo',
            'rut': 'RUT',
            'email': 'Correo electrónico',
            'phone': 'Teléfono',
            'career': 'Carrera',
            'schedule': 'Jornada',
            'observations': 'Observaciones',
        }
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre completo',
            }),
            'rut': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12.345.678-9',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+56 9...',
            }),
            'career': forms.Select(attrs={
                'class': 'form-select',
            }),
            'schedule': forms.Select(attrs={
                'class': 'form-select',
            }),
            'observations': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales...',
            }),
        }
