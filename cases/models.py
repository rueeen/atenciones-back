import os
import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from organization.models import Area
from students.models import Student


def case_attachment_path(instance, filename):
    ext = filename.split('.')[-1]
    return f'cases/{instance.case.folio}/{uuid.uuid4().hex}.{ext}'


def validate_file_extension(file_obj):
    allowed = {'.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png'}
    ext = os.path.splitext(file_obj.name)[1].lower()
    if ext not in allowed:
        raise ValidationError('Formato no permitido. Use pdf, doc, docx, jpg, jpeg o png.')


class CaseCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name


class CaseSubcategory(models.Model):
    category = models.ForeignKey(CaseCategory, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=120)

    class Meta:
        unique_together = ('category', 'name')

    def __str__(self):
        return f'{self.category.name} / {self.name}'


class Case(models.Model):
    class Priority(models.TextChoices):
        LOW = 'low', 'Baja'
        MEDIUM = 'medium', 'Media'
        HIGH = 'high', 'Alta'
        URGENT = 'urgent', 'Urgente'

    class Status(models.TextChoices):
        OPEN = 'open', 'Abierto'
        IN_REVIEW = 'in_review', 'En revisión'
        TRANSFERRED = 'transferred', 'Derivado'
        PENDING_INFO = 'pending_info', 'Pendiente de información'
        PENDING_AREA = 'pending_area', 'Pendiente de otra área'
        RESOLVED = 'resolved', 'Resuelto'
        CLOSED = 'closed', 'Cerrado'
        REJECTED = 'rejected', 'Rechazado'

    folio = models.CharField(max_length=20, unique=True, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(CaseCategory, on_delete=models.PROTECT, related_name='cases')
    subcategory = models.ForeignKey(CaseSubcategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='cases')
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name='cases')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='cases_created')
    origin_area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name='origin_cases')
    current_area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name='assigned_cases')
    current_assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='cases_assigned')
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    due_date = models.DateField(null=True, blank=True)
    final_resolution = models.TextField(blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.folio} - {self.title}'

    def save(self, *args, **kwargs):
        if not self.folio:
            today = timezone.localdate()
            prefix = f'CAS-{today.strftime("%Y%m")}-'
            count = Case.objects.filter(folio__startswith=prefix).count() + 1
            self.folio = f'{prefix}{count:04d}'
        if self.status in {self.Status.CLOSED, self.Status.RESOLVED, self.Status.REJECTED} and not self.closed_at:
            self.closed_at = timezone.now()
        super().save(*args, **kwargs)


class CaseAttachment(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to=case_attachment_path, validators=[validate_file_extension])
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='case_attachments')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Adjunto {self.case.folio}'


class CaseComment(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='case_comments')
    comment = models.TextField()
    is_internal = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class CaseTransfer(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='transfers')
    from_area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name='transfers_out')
    to_area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name='transfers_in')
    transferred_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='case_transfers')
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.case.folio}: {self.from_area} → {self.to_area}'


class CaseHistory(models.Model):
    class EventType(models.TextChoices):
        CREATED = 'created', 'Creación'
        STATUS_CHANGED = 'status_changed', 'Cambio de estado'
        ASSIGNEE_CHANGED = 'assignee_changed', 'Cambio de responsable'
        TRANSFERRED = 'transferred', 'Derivación'
        COMMENT = 'comment', 'Comentario'
        ATTACHMENT = 'attachment', 'Adjunto'
        CLOSED = 'closed', 'Cierre'

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='history')
    event_type = models.CharField(max_length=30, choices=EventType.choices)
    description = models.TextField()
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='case_history_events')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
