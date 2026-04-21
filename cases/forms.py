from django import forms
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from cases.models import Case, CaseAttachment, CaseCategory, CaseComment, CaseSubcategory, CaseTransfer


class DateInput(forms.DateInput):
    input_type = 'date'


class CaseForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = [
            'title',
            'description',
            'category',
            'subcategory',
            'student',
            'priority',
            'due_date',
        ]
        labels = {
            'title': 'Título del caso',
            'description': 'Descripción',
            'category': 'Categoría',
            'subcategory': 'Subcategoría',
            'student': 'Estudiante',
            'priority': 'Prioridad',
            'due_date': 'Fecha de vencimiento',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej.: Solicitud de regularización académica'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe el caso con el mayor detalle posible...'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_category',
            }),
            'subcategory': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_subcategory',
            }),
            'student': forms.Select(attrs={
                'class': 'form-select d-none',
                'id': 'id_student',
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select',
            }),
            'due_date': DateInput(attrs={
                'class': 'form-control',
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.fields['subcategory'].queryset = CaseSubcategory.objects.none()
        self.fields['subcategory'].required = False
        self.fields['due_date'].required = False

        self.fields['title'].help_text = 'Resume el motivo principal del caso.'
        self.fields['description'].help_text = 'Incluye contexto, acciones realizadas y antecedentes relevantes.'
        self.fields['subcategory'].help_text = 'Seleccione una categoría primero.'
        self.fields['student'].help_text = 'Seleccione un estudiante desde el buscador.'

        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['subcategory'].queryset = CaseSubcategory.objects.filter(
                    category_id=category_id
                ).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.category_id:
            self.fields['subcategory'].queryset = CaseSubcategory.objects.filter(
                category=self.instance.category
            ).order_by('name')

        if user:
            self.fields['student'].queryset = self.fields['student'].queryset.select_related()

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        subcategory = cleaned_data.get('subcategory')

        if subcategory and category and subcategory.category_id != category.id:
            self.add_error(
                'subcategory', 'La subcategoría no pertenece a la categoría seleccionada.')

        return cleaned_data


class CategoryForm(forms.ModelForm):
    class Meta:
        model = CaseCategory
        fields = ['name']
        labels = {'name': 'Nombre'}


class SubcategoryForm(forms.ModelForm):
    class Meta:
        model = CaseSubcategory
        fields = ['category', 'name']
        labels = {'category': 'Categoría', 'name': 'Nombre'}


class CaseTransferForm(forms.ModelForm):
    to_area = forms.ModelChoiceField(queryset=None)

    class Meta:
        model = CaseTransfer
        fields = ['to_area', 'note']

    def __init__(self, *args, **kwargs):
        areas_qs = kwargs.pop('areas_qs')
        super().__init__(*args, **kwargs)
        self.fields['to_area'].queryset = areas_qs
        self.fields['to_area'].label = 'Área de destino'
        self.fields['note'].required = True
        self.fields['note'].label = 'Motivo de la derivación'


class ReassignCaseForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ['current_assignee', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['current_assignee'].queryset = User.objects.filter(
            is_active=True)


class CaseCommentForm(forms.ModelForm):
    class Meta:
        model = CaseComment
        fields = ['comment', 'is_internal']
        labels = {'comment': 'Comentario', 'is_internal': 'Comentario interno'}


class CaseAttachmentForm(forms.ModelForm):
    class Meta:
        model = CaseAttachment
        fields = ['file']
        labels = {'file': 'Archivo adjunto'}


class CaseCloseForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ['status', 'final_resolution']
        labels = {'status': 'Estado final',
                  'final_resolution': 'Resolución final'}

    def clean_status(self):
        status = self.cleaned_data['status']
        if status not in {Case.Status.RESOLVED, Case.Status.CLOSED, Case.Status.REJECTED}:
            raise forms.ValidationError(
                'Solo puede cerrar con estado Resuelto, Cerrado o Rechazado.')
        return status
