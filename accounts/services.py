from django.db.models import Q

from accounts.models import UserProfile
from cases.models import Case

CASE_CREATOR_ROLES = {
    UserProfile.Role.VRS,
    UserProfile.Role.DAC,
    UserProfile.Role.DC,
    UserProfile.Role.CC,
    UserProfile.Role.DAE,
    UserProfile.Role.SCHOLARSHIP_MANAGER,
    UserProfile.Role.EMPLOYABILITY_MANAGER,
    UserProfile.Role.CURRICULAR_HEAD,
    UserProfile.Role.CURRICULAR_ASSISTANT,
    UserProfile.Role.LOCAL_NETWORK_ADMIN,
    UserProfile.Role.TECHNICAL_OPERATOR,
    UserProfile.Role.SUBDIRECTOR,
    UserProfile.Role.TUTOR,
    UserProfile.Role.HEAD_TUTOR,
}

ACADEMIC_SCOPED_ROLES = {
    UserProfile.Role.DC,
    UserProfile.Role.CC,
    UserProfile.Role.CURRICULAR_HEAD,
    UserProfile.Role.CURRICULAR_ASSISTANT,
}

SUPERVISION_ROLES = {
    UserProfile.Role.VRS,
    UserProfile.Role.DAC,
    UserProfile.Role.DAE,
    UserProfile.Role.SUBDIRECTOR,
}


def _user_role(user):
    profile = getattr(user, 'profile', None)
    return getattr(profile, 'role', None)


def can_manage_case(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return _user_role(user) in CASE_CREATOR_ROLES


def can_transfer_or_reassign(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return _user_role(user) in SUPERVISION_ROLES


def can_close_case(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return _user_role(user) in CASE_CREATOR_ROLES


def visible_cases_for(user):
    if user.is_superuser:
        return Case.objects.all()

    profile = getattr(user, 'profile', None)
    if not profile:
        return Case.objects.none()

    if profile.role in SUPERVISION_ROLES:
        return Case.objects.all()

    if profile.role in ACADEMIC_SCOPED_ROLES:
        career_ids = list(profile.careers.values_list('id', flat=True))
        if career_ids:
            return Case.objects.filter(student__career_id__in=career_ids).distinct()
        if profile.academic_area_id:
            return Case.objects.filter(student__career__academic_area=profile.academic_area).distinct()
        return Case.objects.none()

    if profile.role in CASE_CREATOR_ROLES:
        return Case.objects.filter(Q(current_area=profile.area) | Q(created_by=user)).distinct()

    return Case.objects.none()
