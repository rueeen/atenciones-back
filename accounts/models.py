from django.conf import settings
from django.core.exceptions import ValidationError
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
    careers = models.ManyToManyField(
        'organization.Career',
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

    @property
    def is_academic_role(self):
        return self.role in {
            self.Role.CAREER_DIRECTOR,
            self.Role.CAREER_COORDINATOR,
        }

    def clean(self):
        errors = {}

        if self.academic_area and self.academic_area.area_id != self.area_id:
            errors['academic_area'] = 'El área académica debe pertenecer al área general seleccionada.'

        if not self.is_academic_role and self.academic_area_id:
            errors['academic_area'] = 'Solo los roles académicos pueden tener área académica.'

        if self.pk and not self.is_academic_role and self.careers.exists():
            errors['careers'] = 'Solo los roles académicos pueden tener carreras asociadas.'

        if self.pk and self.academic_area_id and self.careers.exclude(academic_area_id=self.academic_area_id).exists():
            errors['careers'] = 'Todas las carreras deben pertenecer al área académica seleccionada.'

        if errors:
            raise ValidationError(errors)
