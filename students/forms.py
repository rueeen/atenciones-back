from django import forms
from students.models import Student
from organization.models import AcademicArea, Career


class StudentForm(forms.ModelForm):
    academic_area = forms.ModelChoiceField(
        queryset=AcademicArea.objects.select_related('area').order_by('name'),
        required=False,
        label='Área académica',
        empty_label='Seleccione un área académica',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Student
        fields = [
            'full_name',
            'rut',
            'email',
            'phone',
            'academic_area',
            'career',
            'schedule',
            'observations',
        ]
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
            'career': forms.Select(attrs={'class': 'form-select'}),
            'schedule': forms.Select(attrs={'class': 'form-select'}),
            'observations': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales...',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['career'].queryset = Career.objects.none()
        self.fields['career'].empty_label = 'Seleccione una carrera'

        if self.instance and self.instance.pk and self.instance.career:
            selected_academic_area = self.instance.career.academic_area
            self.fields['academic_area'].initial = selected_academic_area
            self.fields['career'].queryset = Career.objects.filter(
                academic_area=selected_academic_area
            ).order_by('name')

        elif self.data.get('academic_area'):
            try:
                academic_area_id = int(self.data.get('academic_area'))
                self.fields['career'].queryset = Career.objects.filter(
                    academic_area_id=academic_area_id
                ).order_by('name')
            except (TypeError, ValueError):
                self.fields['career'].queryset = Career.objects.none()
