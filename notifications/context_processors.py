from django.db.utils import OperationalError, ProgrammingError

from notifications.models import Notification


def unread_notifications(request):
    if not request.user.is_authenticated:
        return {'unread_notifications_count': 0}

    try:
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False,
        ).count()
    except (OperationalError, ProgrammingError):
        # Database is not fully migrated yet (e.g. missing notifications table).
        unread_count = 0

    return {'unread_notifications_count': unread_count}
