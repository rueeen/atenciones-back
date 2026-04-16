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


class CategoryForm(forms.ModelForm):
    class Meta:
        model = CaseCategory
        fields = ['name']


class SubcategoryForm(forms.ModelForm):
    class Meta:
        model = CaseSubcategory
        fields = ['category', 'name']


class CaseTransferForm(forms.ModelForm):
    to_area = forms.ModelChoiceField(queryset=None)

    class Meta:
        model = CaseTransfer
        fields = ['to_area', 'note']

    def __init__(self, *args, **kwargs):
        areas_qs = kwargs.pop('areas_qs')
        super().__init__(*args, **kwargs)
        self.fields['to_area'].queryset = areas_qs
        self.fields['note'].required = True


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


class CaseAttachmentForm(forms.ModelForm):
    class Meta:
        model = CaseAttachment
        fields = ['file']


class CaseCloseForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ['status', 'final_resolution']

    def clean_status(self):
        status = self.cleaned_data['status']
        if status not in {Case.Status.RESOLVED, Case.Status.CLOSED, Case.Status.REJECTED}:
            raise forms.ValidationError('Solo puede cerrar con estado Resuelto, Cerrado o Rechazado.')
        return status
