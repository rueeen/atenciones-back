from django.db.models import Q

from accounts.models import UserProfile
from psychopedagogy.models import PsychopedagogyRecord


ALLOWED_ROLE_ACCESS = {
    UserProfile.Role.ADMIN,
    UserProfile.Role.SUPERVISOR,
    UserProfile.Role.STAFF,
}


SUPERVISOR_ROLE_ACCESS = {
    UserProfile.Role.ADMIN,
    UserProfile.Role.SUPERVISOR,
}


def _user_role(user):
    profile = getattr(user, 'profile', None)
    return getattr(profile, 'role', None)


def can_access_psychopedagogy_module(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if user.has_perm('psychopedagogy.access_psychopedagogy_module'):
        return True
    return _user_role(user) in ALLOWED_ROLE_ACCESS


def can_view_all_psychopedagogy_records(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if user.has_perm('psychopedagogy.view_all_psychopedagogy_records'):
        return True
    return _user_role(user) in SUPERVISOR_ROLE_ACCESS


def visible_psychopedagogy_records_for(user):
    if not can_access_psychopedagogy_module(user):
        return PsychopedagogyRecord.objects.none()

    if can_view_all_psychopedagogy_records(user):
        return PsychopedagogyRecord.objects.all()

    return PsychopedagogyRecord.objects.filter(
        Q(responsible_tutor=user) |
        Q(created_by=user) |
        Q(authorized_users__user=user)
    ).distinct()


def can_edit_psychopedagogy_record(user, record):
    if not can_access_psychopedagogy_module(user):
        return False
    if can_view_all_psychopedagogy_records(user):
        return True
    if record.responsible_tutor_id == user.id or record.created_by_id == user.id:
        return True
    return record.authorized_users.filter(user=user, can_edit=True).exists()
