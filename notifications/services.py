from django.contrib.auth import get_user_model
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from accounts.services import visible_cases_for
from cases.models import CaseAttachment, CaseComment, CaseTransfer
from notifications.models import Notification
from psychopedagogy.models import PsychopedagogyAttachment, PsychopedagogyLogEntry, PsychopedagogyRecord
from psychopedagogy.services import visible_psychopedagogy_records_for

User = get_user_model()


def _dedupe_users(users):
    unique = []
    seen = set()
    for user in users:
        if not user or not getattr(user, 'is_active', False):
            continue
        if user.pk in seen:
            continue
        seen.add(user.pk)
        unique.append(user)
    return unique


def _can_user_see_case(user, case):
    return visible_cases_for(user).filter(pk=case.pk).exists()


def _can_user_see_record(user, record):
    return visible_psychopedagogy_records_for(user).filter(pk=record.pk).exists()


def create_notification(
    *,
    user,
    title,
    message,
    notification_type,
    action_url='',
    case=None,
    psychopedagogy_record=None,
    psychopedagogy_log_entry=None,
):
    if not user or not user.is_authenticated or not user.is_active:
        return None

    if case and not _can_user_see_case(user, case):
        return None

    if psychopedagogy_record and not _can_user_see_record(user, psychopedagogy_record):
        return None

    if psychopedagogy_log_entry and not _can_user_see_record(user, psychopedagogy_log_entry.record):
        return None

    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        action_url=action_url,
        case=case,
        psychopedagogy_record=psychopedagogy_record,
        psychopedagogy_log_entry=psychopedagogy_log_entry,
    )


def _users_in_area(area):
    return User.objects.filter(profile__area=area, is_active=True).distinct()


def notify_case_created(case):
    area_users = _users_in_area(case.current_area)
    recipients = _dedupe_users([case.created_by, *area_users])
    action_url = reverse('cases:detail', kwargs={'pk': case.pk})

    for user in recipients:
        create_notification(
            user=user,
            title=f'Nuevo caso {case.folio}',
            message='Se registró un nuevo caso en tu área o de tu autoría.',
            notification_type=Notification.NotificationType.CASE_CREATED,
            action_url=action_url,
            case=case,
        )


def notify_case_assigned(case, actor):
    recipients = _dedupe_users([case.created_by, case.current_assignee])
    action_url = reverse('cases:detail', kwargs={'pk': case.pk})
    for user in recipients:
        create_notification(
            user=user,
            title=f'Caso {case.folio} asignado',
            message=f'El caso fue tomado/asignado por {actor.get_full_name() or actor.username}.',
            notification_type=Notification.NotificationType.CASE_ASSIGNED,
            action_url=action_url,
            case=case,
        )


def notify_case_transferred(case, transfer: CaseTransfer, previous_assignee=None):
    to_area_users = _users_in_area(transfer.to_area)
    recipients = _dedupe_users([case.created_by, previous_assignee, *to_area_users])
    action_url = reverse('cases:detail', kwargs={'pk': case.pk})
    for user in recipients:
        create_notification(
            user=user,
            title=f'Caso {case.folio} transferido',
            message='Hay una actualización en un caso asignado a tu área.',
            notification_type=Notification.NotificationType.CASE_TRANSFERRED,
            action_url=action_url,
            case=case,
        )


def notify_case_closed(case):
    recipients = _dedupe_users([case.created_by, case.current_assignee])
    action_url = reverse('cases:detail', kwargs={'pk': case.pk})
    for user in recipients:
        create_notification(
            user=user,
            title=f'Caso {case.folio} cerrado',
            message=f'El caso cambió a estado {case.get_status_display()}.',
            notification_type=Notification.NotificationType.CASE_CLOSED,
            action_url=action_url,
            case=case,
        )


def notify_case_comment_added(comment: CaseComment):
    case = comment.case
    recipients = _dedupe_users([case.created_by, case.current_assignee])
    action_url = reverse('cases:detail', kwargs={'pk': case.pk})
    for user in recipients:
        if user.pk == comment.author_id:
            continue
        create_notification(
            user=user,
            title=f'Nuevo comentario en {case.folio}',
            message='Se agregó un comentario en un caso relacionado contigo.',
            notification_type=Notification.NotificationType.CASE_COMMENT,
            action_url=action_url,
            case=case,
        )


def notify_case_attachment_added(attachment: CaseAttachment):
    case = attachment.case
    recipients = _dedupe_users([case.created_by, case.current_assignee])
    action_url = reverse('cases:detail', kwargs={'pk': case.pk})
    for user in recipients:
        if user.pk == attachment.uploaded_by_id:
            continue
        create_notification(
            user=user,
            title=f'Nuevo adjunto en {case.folio}',
            message='Se agregó un adjunto en un caso relacionado contigo.',
            notification_type=Notification.NotificationType.CASE_ATTACHMENT,
            action_url=action_url,
            case=case,
        )


def _record_recipients(record: PsychopedagogyRecord):
    recipients = [record.created_by, record.responsible_tutor]
    recipients.extend(access.user for access in record.authorized_users.select_related('user'))
    return _dedupe_users(recipients)



def notify_psychopedagogy_record_created(record: PsychopedagogyRecord):
    recipients = _record_recipients(record)
    action_url = reverse('psychopedagogy:detail', kwargs={'pk': record.pk})
    for user in recipients:
        if user.pk == record.created_by_id:
            continue
        create_notification(
            user=user,
            title='Nueva ficha psicopedagógica',
            message='Se creó una nueva ficha psicopedagógica autorizada.',
            notification_type=Notification.NotificationType.PSY_RECORD_UPDATED,
            action_url=action_url,
            psychopedagogy_record=record,
        )


def notify_psychopedagogy_log_created(log_entry: PsychopedagogyLogEntry):
    record = log_entry.record
    recipients = _record_recipients(record)
    action_url = reverse('psychopedagogy:detail', kwargs={'pk': record.pk})
    confidential_message = 'Se agregó una nueva bitácora a un registro autorizado.'
    regular_message = f'Se registró una bitácora: {log_entry.title}.'

    for user in recipients:
        if user.pk == log_entry.author_id:
            continue
        create_notification(
            user=user,
            title='Nueva bitácora psicopedagógica',
            message=confidential_message if record.is_confidential else regular_message,
            notification_type=Notification.NotificationType.PSY_LOG_CREATED,
            action_url=action_url,
            psychopedagogy_record=record,
            psychopedagogy_log_entry=log_entry,
        )


def notify_psychopedagogy_attachment_added(attachment: PsychopedagogyAttachment):
    record = attachment.record
    recipients = _record_recipients(record)
    action_url = reverse('psychopedagogy:detail', kwargs={'pk': record.pk})
    for user in recipients:
        if user.pk == attachment.uploaded_by_id:
            continue
        create_notification(
            user=user,
            title='Nuevo adjunto psicopedagógico',
            message='Se agregó un nuevo adjunto a un registro autorizado.' if record.is_confidential else 'Se agregó un adjunto a la ficha psicopedagógica.',
            notification_type=Notification.NotificationType.PSY_ATTACHMENT,
            action_url=action_url,
            psychopedagogy_record=record,
        )


def notify_psychopedagogy_record_updated(record: PsychopedagogyRecord, actor):
    recipients = _record_recipients(record)
    action_url = reverse('psychopedagogy:detail', kwargs={'pk': record.pk})
    for user in recipients:
        if user.pk == actor.pk:
            continue
        create_notification(
            user=user,
            title='Ficha psicopedagógica actualizada',
            message='Se actualizó una ficha psicopedagógica autorizada.',
            notification_type=Notification.NotificationType.PSY_RECORD_UPDATED,
            action_url=action_url,
            psychopedagogy_record=record,
        )


def mark_all_as_read_for_user(user):
    with transaction.atomic():
        return Notification.objects.filter(user=user, is_read=False).update(
            is_read=True,
            read_at=timezone.now(),
        )
