from django import forms
from students.models import Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['full_name', 'rut', 'email', 'phone', 'career', 'schedule', 'observations']
