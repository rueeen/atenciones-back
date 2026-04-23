from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class UserProfile(models.Model):
    class Role(models.TextChoices):
        VRS = 'vrs', 'Vicerrector sede (VRS)'
        DAC = 'dac', 'Director académico (DAC)'
        DC = 'dc', 'Director de carrera (DC)'
        CC = 'cc', 'Coordinador de carrera (CC)'
        DAE = 'dae', 'Director asuntos estudiantiles (DAE)'
        SCHOLARSHIP_MANAGER = 'scholarship_manager', 'Encargado becas'
        EMPLOYABILITY_MANAGER = 'employability_manager', 'Encargado empleabilidad'
        CURRICULAR_HEAD = 'curricular_head', 'Jefe curricular'
        CURRICULAR_ASSISTANT = 'curricular_assistant', 'Asistente curricular'
        LOCAL_NETWORK_ADMIN = 'local_network_admin', 'Administrador de red local'
        TECHNICAL_OPERATOR = 'technical_operator', 'Operador técnico'
        SUBDIRECTOR = 'subdirector', 'Subdirector'
        TUTOR = 'tutor', 'Tutora'
        HEAD_TUTOR = 'head_tutor', 'Jefa tutora'

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
        default=Role.TECHNICAL_OPERATOR
    )

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} - {self.get_role_display()}'

    @property
    def is_academic_role(self):
        return self.role in {
            self.Role.DC,
            self.Role.CC,
            self.Role.CURRICULAR_HEAD,
            self.Role.CURRICULAR_ASSISTANT,
        }

    def clean(self):
        errors = {}

        if self.academic_area and self.academic_area.area_id != self.area_id:
            errors['academic_area'] = 'El área académica debe pertenecer al área general seleccionada.'

        if not self.is_academic_role and self.academic_area_id:
            errors['academic_area'] = 'Solo los cargos académicos pueden tener área académica.'

        if self.pk and not self.is_academic_role and self.careers.exists():
            errors['careers'] = 'Solo los cargos académicos pueden tener carreras asociadas.'

        if self.pk and self.academic_area_id and self.careers.exclude(academic_area_id=self.academic_area_id).exists():
            errors['careers'] = 'Todas las carreras deben pertenecer al área académica seleccionada.'

        if errors:
            raise ValidationError(errors)
