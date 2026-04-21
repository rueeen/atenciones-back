from django import forms
from django.contrib.auth.models import User
from cases.models import Case, CaseAttachment, CaseCategory, CaseComment, CaseSubcategory, CaseTransfer


class CaseForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = [
            'title', 'description', 'category', 'subcategory', 'student',
            'current_area', 'current_assignee', 'priority', 'status', 'due_date'
        ]
        labels = {
            'title': 'Título',
            'description': 'Descripción',
            'category': 'Categoría',
            'subcategory': 'Subcategoría',
            'student': 'Estudiante',
            'current_area': 'Área actual',
            'current_assignee': 'Responsable actual',
            'priority': 'Prioridad',
            'status': 'Estado',
            'due_date': 'Fecha de vencimiento',
        }


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
        self.fields['current_assignee'].queryset = User.objects.filter(is_active=True)


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
        labels = {'status': 'Estado final', 'final_resolution': 'Resolución final'}

    def clean_status(self):
        status = self.cleaned_data['status']
        if status not in {Case.Status.RESOLVED, Case.Status.CLOSED, Case.Status.REJECTED}:
            raise forms.ValidationError('Solo puede cerrar con estado Resuelto, Cerrado o Rechazado.')
        return status
