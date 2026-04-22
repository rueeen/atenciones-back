from psychopedagogy.models import (
    PsychopedagogyAttachment,
    PsychopedagogyLogEntry,
    PsychopedagogyRecord,
)
from psychopedagogy.models import PsychopedagogyRecord
from django import forms
from django.contrib.auth.models import User

from psychopedagogy.models import PsychopedagogyAttachment, PsychopedagogyLogEntry, PsychopedagogyRecord


class DateInput(forms.DateInput):
    input_type = 'date'


class DateInput(forms.DateInput):
    input_type = 'date'


class PsychopedagogyRecordForm(forms.ModelForm):
    class Meta:
        model = PsychopedagogyRecord
        fields = [
            'student',
            'responsible_tutor',
            'status',
            'start_date',
            'end_date',
            'support_category',
            'support_reason',
            'background_notes',
            'summary',
            'observations',
            'is_confidential',
        ]
        labels = {
            'student': 'Estudiante',
            'responsible_tutor': 'Tutora responsable',
            'status': 'Estado',
            'start_date': 'Fecha de inicio',
            'end_date': 'Fecha de cierre',
            'support_category': 'Categoría de apoyo',
            'support_reason': 'Motivo de acompañamiento',
            'background_notes': 'Antecedentes reportados',
            'summary': 'Resumen general',
            'observations': 'Observaciones',
            'is_confidential': 'Información confidencial',
        }
        widgets = {
            'student': forms.Select(attrs={
                'class': 'form-select d-none',
                'id': 'id_student',
            }),
            'responsible_tutor': forms.Select(attrs={
                'class': 'form-select',
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
            'start_date': DateInput(attrs={
                'class': 'form-control',
            }),
            'end_date': DateInput(attrs={
                'class': 'form-control',
            }),
            'support_category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej.: apoyo académico, acompañamiento emocional, seguimiento',
            }),
            'support_reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe el motivo de acompañamiento',
            }),
            'background_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Antecedentes reportados relevantes',
            }),
            'summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Resumen general de la ficha',
            }),
            'observations': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].help_text = 'Seleccione un estudiante desde el buscador.'
        self.fields['end_date'].required = False
        self.fields['support_category'].required = False
        self.fields['background_notes'].required = False
        self.fields['summary'].required = False
        self.fields['observations'].required = False


class PsychopedagogyLogEntryForm(forms.ModelForm):
    class Meta:
        model = PsychopedagogyLogEntry
        fields = [
            'entry_date',
            'entry_type',
            'title',
            'content',
            'agreements',
            'next_follow_up',
        ]
        widgets = {
            'entry_date': DateInput(attrs={'class': 'form-control'}),
            'entry_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'agreements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'next_follow_up': DateInput(attrs={'class': 'form-control'}),
        }


class PsychopedagogyAttachmentForm(forms.ModelForm):
    class Meta:
        model = PsychopedagogyAttachment
        fields = ['attachment_type', 'file', 'note']
        widgets = {
            'attachment_type': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'note': forms.TextInput(attrs={'class': 'form-control'}),
        }


class PsychopedagogyLogEntryForm(forms.ModelForm):
    class Meta:
        model = PsychopedagogyLogEntry
        fields = ['entry_date', 'entry_type', 'title',
                  'content', 'agreements', 'next_follow_up']
        widgets = {
            'entry_date': DateInput(attrs={'class': 'form-control'}),
            'next_follow_up': DateInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'rows': 4}),
            'agreements': forms.Textarea(attrs={'rows': 3}),
        }


class PsychopedagogyAttachmentForm(forms.ModelForm):
    class Meta:
        model = PsychopedagogyAttachment
        fields = ['attachment_type', 'file', 'note']
        widgets = {
            'note': forms.TextInput(attrs={'placeholder': 'Observación breve del documento'}),
        }
