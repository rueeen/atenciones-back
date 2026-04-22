from django import forms
from django.contrib.auth.models import User
from accounts.models import UserProfile


class UserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
            'password': 'Contraseña',
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['area', 'role', 'academic_area', 'careers']
        labels = {
            'area': 'Área',
            'role': 'Rol',
            'academic_area': 'Área académica',
            'careers': 'Carreras',
        }

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        area = cleaned_data.get('area')
        academic_area = cleaned_data.get('academic_area')
        careers = cleaned_data.get('careers')

        academic_roles = {
            UserProfile.Role.CAREER_DIRECTOR,
            UserProfile.Role.CAREER_COORDINATOR,
        }

        if academic_area and area and academic_area.area_id != area.id:
            self.add_error('academic_area', 'El área académica no pertenece al área general seleccionada.')

        if role not in academic_roles:
            if academic_area:
                self.add_error('academic_area', 'Este rol no debe tener área académica.')
            if careers:
                self.add_error('careers', 'Este rol no debe tener carreras asociadas.')
        elif careers and academic_area and careers.exclude(academic_area=academic_area).exists():
            self.add_error('careers', 'Todas las carreras deben pertenecer al área académica seleccionada.')

        return cleaned_data
