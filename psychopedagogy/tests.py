from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserProfile
from organization.models import AcademicArea, Area, Career
from psychopedagogy.models import PsychopedagogyRecord
from students.models import Student


class InclusionLogPermissionTest(TestCase):
    def setUp(self):
        self.area = Area.objects.create(name='DAE')
        self.academic_root = Area.objects.create(name='Dirección Académica')
        self.academic_area = AcademicArea.objects.create(name='Tecnología', area=self.academic_root)
        self.career = Career.objects.create(name='Analista Programador', academic_area=self.academic_area)
        self.student = Student.objects.create(
            full_name='Paz Rojas', rut='18.222.111-9', email='paz@example.com', phone='999', career=self.career
        )

        self.tutora = User.objects.create_user('tutora1', password='test123')
        self.tutora.profile.area = self.area
        self.tutora.profile.role = UserProfile.Role.TUTOR
        self.tutora.profile.save()

        self.jefa_tutora = User.objects.create_user('jefa1', password='test123')
        self.jefa_tutora.profile.area = self.area
        self.jefa_tutora.profile.role = UserProfile.Role.HEAD_TUTOR
        self.jefa_tutora.profile.save()

        self.record = PsychopedagogyRecord.objects.create(
            student=self.student,
            responsible_tutor=self.tutora,
            support_reason='Seguimiento inicial',
            created_by=self.tutora,
        )

    def test_tutora_can_create_log_entries(self):
        self.client.login(username='tutora1', password='test123')
        response = self.client.post(
            reverse('psychopedagogy:add-log', kwargs={'pk': self.record.pk}),
            data={
                'entry_date': '2026-04-23',
                'entry_type': 'session',
                'title': 'Sesión inicial',
                'content': 'Contenido de prueba',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.record.log_entries.count(), 1)

    def test_head_tutor_cannot_create_log_entries(self):
        self.client.login(username='jefa1', password='test123')
        response = self.client.post(
            reverse('psychopedagogy:add-log', kwargs={'pk': self.record.pk}),
            data={
                'entry_date': '2026-04-23',
                'entry_type': 'session',
                'title': 'Intento no autorizado',
                'content': 'Contenido de prueba',
            },
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.record.log_entries.count(), 0)
