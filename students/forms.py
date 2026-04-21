from django import forms
from students.models import Student
from organization.models import AcademicArea, Career


class StudentForm(forms.ModelForm):
    academic_area = forms.ModelChoiceField(
        queryset=AcademicArea.objects.select_related('area').order_by('name'),
        required=True,
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

        self.fields['academic_area'].error_messages['required'] = 'Debe seleccionar un área académica.'
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
        elif self.data.get('career'):
            # Permite mantener la opción seleccionada en el select en caso de
            # formularios inválidos sin área seleccionada.
            try:
                career_id = int(self.data.get('career'))
                selected_career = Career.objects.select_related('academic_area').filter(pk=career_id).first()
                if selected_career:
                    self.fields['career'].queryset = Career.objects.filter(
                        academic_area=selected_career.academic_area
                    ).order_by('name')
            except (TypeError, ValueError):
                self.fields['career'].queryset = Career.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        academic_area = cleaned_data.get('academic_area')
        career = cleaned_data.get('career')

        if academic_area and career and career.academic_area_id != academic_area.id:
            self.add_error(
                'career',
                'La carrera seleccionada no pertenece al área académica escogida.'
            )

        return cleaned_data
