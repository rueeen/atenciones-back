from django import forms
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from cases.models import Case, CaseAttachment, CaseCategory, CaseComment, CaseSubcategory, CaseTransfer
from cases.services import get_allowed_categories_for_user, is_category_allowed_for_user


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
        self.enforce_category_permissions = kwargs.pop('enforce_category_permissions', True)
        self.user = user
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
            if self.enforce_category_permissions:
                self.fields['category'].queryset = get_allowed_categories_for_user(user)

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        subcategory = cleaned_data.get('subcategory')

        if subcategory and category and subcategory.category_id != category.id:
            self.add_error('subcategory', 'La subcategoría no pertenece a la categoría seleccionada.')

        if self.enforce_category_permissions and category and self.user and not is_category_allowed_for_user(self.user, category):
            self.add_error('category', 'No tienes permisos para crear casos con esta categoría.')

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
    class Meta:
        model = CaseTransfer
        fields = ['to_area', 'note']
        labels = {
            'to_area': 'Área de destino',
            'note': 'Motivo de la derivación',
        }
        widgets = {
            'to_area': forms.Select(attrs={'class': 'form-select'}),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Detalle por qué se deriva este caso.',
            }),
        }

    def __init__(self, *args, **kwargs):
        self.case = kwargs.pop('case')
        super().__init__(*args, **kwargs)
        self.fields['to_area'].queryset = self.fields['to_area'].queryset.exclude(
            pk=self.case.current_area_id
        )
        self.fields['to_area'].empty_label = 'Seleccione un área'
        self.fields['note'].required = True
        self.fields['note'].help_text = 'Este motivo quedará registrado en el historial del caso.'

    def clean(self):
        cleaned_data = super().clean()
        if not self.case.can_be_transferred():
            raise forms.ValidationError('No se puede derivar un caso cerrado.')
        return cleaned_data

    def clean_to_area(self):
        to_area = self.cleaned_data['to_area']
        if to_area.pk == self.case.current_area_id:
            raise forms.ValidationError('Debe seleccionar un área distinta al área actual del caso.')
        return to_area

    def clean_note(self):
        note = self.cleaned_data['note'].strip()
        if not note:
            raise forms.ValidationError('Debe ingresar el motivo de la derivación.')
        return note


class CaseTakeForm(forms.Form):
    confirm = forms.BooleanField(required=True, initial=True, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        self.case = kwargs.pop('case')
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if self.case.is_closed:
            raise forms.ValidationError('No se puede tomar un caso cerrado.')
        if self.case.current_assignee_id:
            raise forms.ValidationError('El caso ya tiene responsable asignado.')
        profile = getattr(self.user, 'profile', None)
        if not profile or profile.area_id != self.case.current_area_id:
            raise forms.ValidationError('Solo usuarios del área actual del caso pueden tomarlo.')
        return cleaned_data


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
