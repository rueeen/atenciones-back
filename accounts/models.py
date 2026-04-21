from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrador general'
        SUPERVISOR = 'supervisor', 'Supervisor de área'
        STAFF = 'staff', 'Funcionario'
        CAREER_DIRECTOR = 'career_director', 'Director de carrera'
        CAREER_COORDINATOR = 'career_coordinator', 'Coordinador de carrera'
        READ_ONLY = 'read_only', 'Solo lectura'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    area = models.ForeignKey(
        'organization.Area',
        on_delete=models.PROTECT,
        related_name='profiles'
    )
    academic_area = models.ForeignKey(
        'organization.AcademicArea',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='profiles'
    )
    career = models.ForeignKey(
        'organization.Career',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='profiles'
    )
    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.STAFF
    )

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} - {self.get_role_display()}'
