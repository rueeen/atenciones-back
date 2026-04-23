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
        fields = ['area', 'role', 'careers']
        labels = {
            'area': 'Área',
            'role': 'Cargo',
            'careers': 'Carreras',
        }

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        careers = cleaned_data.get('careers')

        academic_roles = {
            UserProfile.Role.DC,
            UserProfile.Role.CC,
            UserProfile.Role.CURRICULAR_HEAD,
            UserProfile.Role.CURRICULAR_ASSISTANT,
        }

        if role not in academic_roles:
            if careers:
                self.add_error('careers', 'Este cargo no debe tener carreras asociadas.')

        return cleaned_data
