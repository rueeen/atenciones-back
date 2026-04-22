from django import forms
from django.contrib.auth.models import User

from psychopedagogy.models import PsychopedagogyAttachment, PsychopedagogyLogEntry, PsychopedagogyRecord


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
        widgets = {
            'start_date': DateInput(attrs={'class': 'form-control'}),
            'end_date': DateInput(attrs={'class': 'form-control'}),
            'support_reason': forms.Textarea(attrs={'rows': 3}),
            'background_notes': forms.Textarea(attrs={'rows': 3}),
            'summary': forms.Textarea(attrs={'rows': 3}),
            'observations': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['end_date'].required = False
        self.fields['support_category'].required = False
        self.fields['background_notes'].required = False
        self.fields['summary'].required = False
        self.fields['observations'].required = False
        self.fields['responsible_tutor'].queryset = User.objects.filter(is_active=True).order_by('first_name', 'last_name', 'username')

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        status = cleaned_data.get('status')

        if end_date and start_date and end_date < start_date:
            self.add_error('end_date', 'La fecha de cierre no puede ser anterior a la fecha de inicio.')

        if status == PsychopedagogyRecord.Status.CLOSED and not end_date:
            self.add_error('end_date', 'Debe registrar fecha de cierre cuando el estado es Cerrado.')

        return cleaned_data


class PsychopedagogyLogEntryForm(forms.ModelForm):
    class Meta:
        model = PsychopedagogyLogEntry
        fields = ['entry_date', 'entry_type', 'title', 'content', 'agreements', 'next_follow_up']
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
