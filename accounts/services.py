from django.db.models import Q
from cases.models import Case
from accounts.models import UserProfile


def can_manage_case(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    role = getattr(user.profile, 'role', None)
    return role in {
        UserProfile.Role.ADMIN,
        UserProfile.Role.SUPERVISOR,
        UserProfile.Role.STAFF,
        UserProfile.Role.CAREER_DIRECTOR,
        UserProfile.Role.CAREER_COORDINATOR,
    }


def can_transfer_or_reassign(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    role = getattr(user.profile, 'role', None)
    return role in {UserProfile.Role.ADMIN, UserProfile.Role.SUPERVISOR}


def can_close_case(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    role = getattr(user.profile, 'role', None)
    return role in {UserProfile.Role.ADMIN, UserProfile.Role.SUPERVISOR, UserProfile.Role.STAFF}


def visible_cases_for(user):
    if user.is_superuser:
        return Case.objects.all()
    profile = getattr(user, 'profile', None)
    if not profile:
        return Case.objects.none()

    if profile.role == UserProfile.Role.ADMIN:
        return Case.objects.all()
    if profile.role in {UserProfile.Role.SUPERVISOR, UserProfile.Role.STAFF, UserProfile.Role.READ_ONLY}:
        return Case.objects.filter(Q(current_area=profile.area) | Q(created_by=user)).distinct()
    if profile.role == UserProfile.Role.CAREER_DIRECTOR:
        return Case.objects.filter(student__career__academic_area=profile.career.academic_area) if profile.career else Case.objects.none()
    if profile.role == UserProfile.Role.CAREER_COORDINATOR:
        return Case.objects.filter(student__career=profile.career) if profile.career else Case.objects.none()
    return Case.objects.none()
