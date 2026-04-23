from django.conf import settings
from django.db import models
from django.utils import timezone


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        CASE_CREATED = 'case_created', 'Caso creado'
        CASE_ASSIGNED = 'case_assigned', 'Caso asignado'
        CASE_TRANSFERRED = 'case_transferred', 'Caso transferido'
        CASE_CLOSED = 'case_closed', 'Caso cerrado'
        CASE_COMMENT = 'case_comment', 'Comentario en caso'
        CASE_ATTACHMENT = 'case_attachment', 'Adjunto en caso'
        PSY_RECORD_UPDATED = 'psy_record_updated', 'Actualización de ficha psicopedagógica'
        PSY_LOG_CREATED = 'psy_log_created', 'Bitácora psicopedagógica creada'
        PSY_ATTACHMENT = 'psy_attachment', 'Adjunto psicopedagógico'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    title = models.CharField(max_length=180)
    message = models.TextField()
    notification_type = models.CharField(max_length=40, choices=NotificationType.choices)
    action_url = models.CharField(max_length=255, blank=True)
    case = models.ForeignKey(
        'cases.Case',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
    )
    psychopedagogy_record = models.ForeignKey(
        'psychopedagogy.PsychopedagogyRecord',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
    )
    psychopedagogy_log_entry = models.ForeignKey(
        'psychopedagogy.PsychopedagogyLogEntry',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
    )
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
            models.Index(fields=['notification_type', '-created_at']),
        ]

    def mark_as_read(self):
        if self.is_read:
            return
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=['is_read', 'read_at'])

    def __str__(self):
        return f'Notificación para {self.user}: {self.title}'
