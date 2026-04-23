import os
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from students.models import Student


def psychopedagogy_attachment_path(instance, filename):
    ext = filename.split('.')[-1]
    return f'psychopedagogy/{instance.record_id}/{uuid.uuid4().hex}.{ext}'


def validate_attachment_extension(file_obj):
    allowed = {'.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png'}
    ext = os.path.splitext(file_obj.name)[1].lower()
    if ext not in allowed:
        raise ValidationError('Formato no permitido. Use pdf, doc, docx, jpg, jpeg o png.')


class PsychopedagogyRecord(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Activo'
        ON_HOLD = 'on_hold', 'En pausa'
        CLOSED = 'closed', 'Cerrado'

    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name='psychopedagogy_records')
    responsible_tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='psychopedagogy_records_as_tutor',
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    start_date = models.DateField(default=timezone.localdate)
    end_date = models.DateField(null=True, blank=True)
    support_category = models.CharField(max_length=120, blank=True)
    support_reason = models.TextField(verbose_name='Motivo de acompañamiento')
    background_notes = models.TextField(blank=True, verbose_name='Antecedentes reportados')
    summary = models.TextField(blank=True, verbose_name='Resumen general')
    observations = models.TextField(blank=True)
    is_confidential = models.BooleanField(default=True, verbose_name='Información confidencial')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='psychopedagogy_records_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['student'],
                condition=Q(status='active'),
                name='unique_active_psychopedagogy_record_per_student',
            )
        ]
        permissions = [
            ('access_psychopedagogy_module', 'Puede acceder al módulo psicopedagógico'),
            ('view_all_psychopedagogy_records', 'Puede ver todas las fichas psicopedagógicas'),
        ]

    def clean(self):
        super().clean()

        if self.status == self.Status.CLOSED and not self.end_date:
            raise ValidationError(
                {'end_date': 'Debe indicar una fecha de cierre cuando la ficha esté cerrada.'}
            )

        if self.end_date and self.end_date < self.start_date:
            raise ValidationError(
                {'end_date': 'La fecha de cierre no puede ser anterior a la fecha de inicio.'}
            )

        if self.status == self.Status.ACTIVE:
            qs = PsychopedagogyRecord.objects.filter(
                student=self.student,
                status=self.Status.ACTIVE,
            )
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError(
                    {
                        'student': (
                            'El estudiante ya tiene una ficha psicopedagógica activa. '
                            'Registre los nuevos apoyos en la bitácora de esa ficha.'
                        )
                    }
                )

    def __str__(self):
        return f'Ficha #{self.pk} - {self.student}'


class PsychopedagogyRecordAccess(models.Model):
    record = models.ForeignKey(PsychopedagogyRecord, on_delete=models.CASCADE, related_name='authorized_users')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='psychopedagogy_authorizations')
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='psychopedagogy_authorizations_granted',
    )
    can_edit = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('record', 'user')

    def __str__(self):
        return f'Acceso {self.user} a ficha {self.record_id}'


class PsychopedagogyLogEntry(models.Model):
    class EntryType(models.TextChoices):
        SESSION = 'session', 'Sesión'
        FOLLOW_UP = 'follow_up', 'Seguimiento'
        AGREEMENT = 'agreement', 'Acuerdo'
        INCIDENT = 'incident', 'Incidencia'
        OTHER = 'other', 'Otro'

    record = models.ForeignKey(PsychopedagogyRecord, on_delete=models.CASCADE, related_name='log_entries')
    entry_date = models.DateField(default=timezone.localdate)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='psychopedagogy_log_entries')
    entry_type = models.CharField(max_length=20, choices=EntryType.choices)
    title = models.CharField(max_length=180)
    content = models.TextField()
    agreements = models.TextField(blank=True, verbose_name='Acuerdos / acciones')
    next_follow_up = models.DateField(null=True, blank=True, verbose_name='Próximo seguimiento')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-entry_date', '-created_at']

    def __str__(self):
        return f'{self.record_id} - {self.title}'


class PsychopedagogyAttachment(models.Model):
    class AttachmentType(models.TextChoices):
        REPORT = 'report', 'Informe'
        SUPPORT_PLAN = 'support_plan', 'Plan de apoyo'
        OBSERVATION = 'observation', 'Observación'
        OTHER = 'other', 'Otro'

    record = models.ForeignKey(PsychopedagogyRecord, on_delete=models.CASCADE, related_name='attachments')
    attachment_type = models.CharField(max_length=30, choices=AttachmentType.choices, default=AttachmentType.OTHER)
    file = models.FileField(upload_to=psychopedagogy_attachment_path, validators=[validate_attachment_extension])
    note = models.CharField(max_length=255, blank=True, verbose_name='Observación del archivo')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='psychopedagogy_attachments_uploaded')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'Adjunto {self.record_id}'
