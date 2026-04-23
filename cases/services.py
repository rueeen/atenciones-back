from accounts.models import UserProfile
from accounts.services import CASE_CREATOR_ROLES
from cases.models import CaseCategory


# Matriz base de categorías por cargo.
# Pendiente funcional: validar/ajustar esta matriz con negocio para cada sede.
DEFAULT_ROLE_CATEGORY_MAP = {
    UserProfile.Role.VRS: {
        'Becas y beneficios', 'Vida estudiantil', 'Inscripción o matrícula', 'Solicitudes académicas',
        'Certificados', 'Convalidaciones', 'Horarios', 'Titulación', 'Práctica', 'Documentación', 'Otros',
    },
    UserProfile.Role.DAC: {'Solicitudes académicas', 'Convalidaciones', 'Horarios', 'Titulación', 'Certificados', 'Otros'},
    UserProfile.Role.DC: {'Solicitudes académicas', 'Convalidaciones', 'Horarios', 'Práctica', 'Titulación', 'Otros'},
    UserProfile.Role.CC: {'Solicitudes académicas', 'Convalidaciones', 'Horarios', 'Práctica', 'Otros'},
    UserProfile.Role.DAE: {'Becas y beneficios', 'Vida estudiantil', 'Inscripción o matrícula', 'Documentación', 'Otros'},
    UserProfile.Role.SCHOLARSHIP_MANAGER: {'Becas y beneficios', 'Documentación', 'Otros'},
    UserProfile.Role.EMPLOYABILITY_MANAGER: {'Práctica', 'Titulación', 'Solicitudes académicas', 'Otros'},
    UserProfile.Role.CURRICULAR_HEAD: {'Solicitudes académicas', 'Convalidaciones', 'Horarios', 'Titulación', 'Otros'},
    UserProfile.Role.CURRICULAR_ASSISTANT: {'Solicitudes académicas', 'Convalidaciones', 'Horarios', 'Certificados', 'Otros'},
    UserProfile.Role.LOCAL_NETWORK_ADMIN: {'Documentación', 'Otros'},
    UserProfile.Role.TECHNICAL_OPERATOR: {'Documentación', 'Otros'},
    UserProfile.Role.SUBDIRECTOR: {'Becas y beneficios', 'Vida estudiantil', 'Inscripción o matrícula', 'Solicitudes académicas', 'Certificados', 'Convalidaciones', 'Horarios', 'Titulación', 'Práctica', 'Documentación', 'Otros'},
    UserProfile.Role.TUTOR: {'Vida estudiantil', 'Becas y beneficios', 'Solicitudes académicas', 'Otros'},
    UserProfile.Role.HEAD_TUTOR: {'Vida estudiantil', 'Becas y beneficios', 'Solicitudes académicas', 'Otros'},
}


def get_allowed_categories_for_user(user):
    if not user.is_authenticated:
        return CaseCategory.objects.none()

    if user.is_superuser:
        return CaseCategory.objects.all().order_by('name')

    role = getattr(getattr(user, 'profile', None), 'role', None)
    if role not in CASE_CREATOR_ROLES:
        return CaseCategory.objects.none()

    category_names = DEFAULT_ROLE_CATEGORY_MAP.get(role, set())
    if not category_names:
        return CaseCategory.objects.all().order_by('name')

    categories = CaseCategory.objects.filter(name__in=category_names).order_by('name')
    if categories.exists():
        return categories

    # Fallback defensivo: si los nombres definidos no coinciden con BD (p. ej. carga
    # inicial distinta por ambiente), evitamos dejar el selector vacío.
    return CaseCategory.objects.all().order_by('name')


def is_category_allowed_for_user(user, category):
    if not category:
        return False
    return get_allowed_categories_for_user(user).filter(pk=category.pk).exists()


def user_can_create_cases(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    role = getattr(getattr(user, 'profile', None), 'role', None)
    return role in CASE_CREATOR_ROLES
