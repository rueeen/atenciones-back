from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserProfile
from accounts.services import visible_cases_for
from cases.forms import CaseTransferForm
from cases.models import Case, CaseCategory, CaseHistory, CaseTransfer
from organization.models import AcademicArea, Area, Career
from students.models import Student


class CaseModelAndPermissionsTest(TestCase):
    def setUp(self):
        self.area = Area.objects.create(name='DAE')
        self.academic_root = Area.objects.create(name='Dirección Académica', is_academic_direction=True)
        self.academic_area = AcademicArea.objects.create(name='Administración', parent_area=self.academic_root)
        self.career = Career.objects.create(name='Administración de Empresas', academic_area=self.academic_area)
        self.student = Student.objects.create(
            full_name='Ana Pérez', rut='11.111.111-1', email='ana@example.com', phone='123', career=self.career
        )
        self.category = CaseCategory.objects.create(name='Becas y beneficios')
        self.user = User.objects.create_user('func1', password='test123')
        self.user.profile.area = self.area
        self.user.profile.role = UserProfile.Role.STAFF
        self.user.profile.save()

    def test_case_generates_folio(self):
        case = Case.objects.create(
            title='Consulta de beca',
            description='Detalle',
            category=self.category,
            student=self.student,
            created_by=self.user,
            origin_area=self.area,
            current_area=self.area,
        )
        self.assertTrue(case.folio.startswith('CAS-'))

    def test_visible_cases_for_staff(self):
        case = Case.objects.create(
            title='Caso visible',
            description='Detalle',
            category=self.category,
            student=self.student,
            created_by=self.user,
            origin_area=self.area,
            current_area=self.area,
        )
        qs = visible_cases_for(self.user)
        self.assertIn(case, qs)


class CaseTransferFlowTest(TestCase):
    def setUp(self):
        self.area_origin = Area.objects.create(name='Bienestar')
        self.area_destination = Area.objects.create(name='Registro Académico')
        self.academic_root = Area.objects.create(name='Dirección Académica', is_academic_direction=True)
        self.academic_area = AcademicArea.objects.create(name='Informática', parent_area=self.academic_root)
        self.career = Career.objects.create(name='Analista Programador', academic_area=self.academic_area)
        self.student = Student.objects.create(
            full_name='Pedro Díaz', rut='12.222.333-4', email='pedro@example.com', phone='321', career=self.career
        )
        self.category = CaseCategory.objects.create(name='Beneficios')

        self.supervisor = User.objects.create_user('supervisor', password='test123')
        self.supervisor.profile.area = self.area_origin
        self.supervisor.profile.role = UserProfile.Role.SUPERVISOR
        self.supervisor.profile.save()

        self.assignee = User.objects.create_user('responsable', password='test123')

        self.case = Case.objects.create(
            title='Derivación pendiente',
            description='Detalle',
            category=self.category,
            student=self.student,
            created_by=self.supervisor,
            origin_area=self.area_origin,
            current_area=self.area_origin,
            current_assignee=self.assignee,
        )

    def test_transfer_form_rejects_same_area(self):
        form = CaseTransferForm(
            data={'to_area': self.area_origin.pk, 'note': 'Necesita revisión.'},
            case=self.case,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('to_area', form.errors)

    def test_transfer_updates_case_and_history(self):
        self.client.login(username='supervisor', password='test123')

        response = self.client.post(
            reverse('cases:transfer', kwargs={'pk': self.case.pk}),
            data={'to_area': self.area_destination.pk, 'note': 'Derivación por competencia funcional.'},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        self.case.refresh_from_db()
        self.assertEqual(self.case.current_area, self.area_destination)
        self.assertEqual(self.case.status, Case.Status.TRANSFERRED)
        self.assertIsNone(self.case.current_assignee)

        transfer = CaseTransfer.objects.get(case=self.case)
        self.assertEqual(transfer.from_area, self.area_origin)
        self.assertEqual(transfer.to_area, self.area_destination)
        self.assertEqual(transfer.transferred_by, self.supervisor)

        history_event = CaseHistory.objects.filter(
            case=self.case,
            event_type=CaseHistory.EventType.TRANSFERRED,
        ).first()
        self.assertIsNotNone(history_event)
