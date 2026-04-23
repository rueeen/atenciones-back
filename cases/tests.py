from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserProfile
from accounts.services import visible_cases_for
from cases.forms import CaseTransferForm
from cases.models import Case, CaseCategory, CaseHistory, CaseSubcategory, CaseTransfer
from organization.models import AcademicArea, Area, Career
from students.models import Student


class CaseModelAndPermissionsTest(TestCase):
    def setUp(self):
        self.area = Area.objects.create(name='DAE')
        self.academic_root = Area.objects.create(name='Dirección Académica')
        self.academic_area = AcademicArea.objects.create(name='Administración', area=self.academic_root)
        self.career = Career.objects.create(name='Administración de Empresas', academic_area=self.academic_area)
        self.student = Student.objects.create(
            full_name='Ana Pérez', rut='11.111.111-1', email='ana@example.com', phone='123', career=self.career
        )
        self.category = CaseCategory.objects.create(name='Becas y beneficios')
        self.user = User.objects.create_user('func1', password='test123')
        self.user.profile.area = self.area
        self.user.profile.role = UserProfile.Role.TECHNICAL_OPERATOR
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
        self.academic_root = Area.objects.create(name='Dirección Académica')
        self.academic_area = AcademicArea.objects.create(name='Informática', area=self.academic_root)
        self.career = Career.objects.create(name='Analista Programador', academic_area=self.academic_area)
        self.student = Student.objects.create(
            full_name='Pedro Díaz', rut='12.222.333-4', email='pedro@example.com', phone='321', career=self.career
        )
        self.category = CaseCategory.objects.create(name='Beneficios')

        self.staff_origin = User.objects.create_user('staff_origin', password='test123')
        self.staff_origin.profile.area = self.area_origin
        self.staff_origin.profile.role = UserProfile.Role.TECHNICAL_OPERATOR
        self.staff_origin.profile.save()

        self.staff_destination = User.objects.create_user('staff_destination', password='test123')
        self.staff_destination.profile.area = self.area_destination
        self.staff_destination.profile.role = UserProfile.Role.TECHNICAL_OPERATOR
        self.staff_destination.profile.save()

        self.assignee = User.objects.create_user('responsable', password='test123')

        self.case = Case.objects.create(
            title='Derivación pendiente',
            description='Detalle',
            category=self.category,
            student=self.student,
            created_by=self.staff_origin,
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
        self.client.login(username='staff_origin', password='test123')

        response = self.client.post(
            reverse('cases:transfer', kwargs={'pk': self.case.pk}),
            data={'to_area': self.area_destination.pk, 'note': 'Derivación por competencia funcional.'},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        self.case.refresh_from_db()
        self.assertEqual(self.case.current_area, self.area_destination)
        self.assertEqual(self.case.status, Case.Status.PENDING_AREA)
        self.assertIsNone(self.case.current_assignee)

        transfer = CaseTransfer.objects.get(case=self.case)
        self.assertEqual(transfer.from_area, self.area_origin)
        self.assertEqual(transfer.to_area, self.area_destination)
        self.assertEqual(transfer.transferred_by, self.staff_origin)

        history_event = CaseHistory.objects.filter(
            case=self.case,
            event_type=CaseHistory.EventType.TRANSFERRED,
        ).first()
        self.assertIsNotNone(history_event)

    def test_destination_area_user_can_take_case(self):
        self.client.login(username='staff_origin', password='test123')
        self.client.post(
            reverse('cases:transfer', kwargs={'pk': self.case.pk}),
            data={'to_area': self.area_destination.pk, 'note': 'Derivación por competencia funcional.'},
            follow=True,
        )

        self.client.logout()
        self.client.login(username='staff_destination', password='test123')
        response = self.client.post(
            reverse('cases:take', kwargs={'pk': self.case.pk}),
            data={'confirm': True},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.case.refresh_from_db()
        self.assertEqual(self.case.current_assignee, self.staff_destination)
        self.assertEqual(self.case.status, Case.Status.IN_REVIEW)
        self.assertTrue(CaseHistory.objects.filter(
            case=self.case,
            event_type=CaseHistory.EventType.ASSIGNEE_CHANGED,
        ).exists())

    def test_cannot_take_case_from_other_area(self):
        outsider = User.objects.create_user('outsider', password='test123')
        outsider.profile.area = self.area_origin
        outsider.profile.role = UserProfile.Role.TECHNICAL_OPERATOR
        outsider.profile.save()

        self.case.current_assignee = None
        self.case.current_area = self.area_destination
        self.case.status = Case.Status.PENDING_AREA
        self.case.save()

        self.client.login(username='outsider', password='test123')
        self.client.post(
            reverse('cases:take', kwargs={'pk': self.case.pk}),
            data={'confirm': True},
            follow=True,
        )
        self.case.refresh_from_db()
        self.assertIsNone(self.case.current_assignee)


class CaseCreationPermissionTest(TestCase):
    def setUp(self):
        self.area = Area.objects.create(name='DAE')
        self.academic_root = Area.objects.create(name='Dirección Académica')
        self.academic_area = AcademicArea.objects.create(name='Tecnología', area=self.academic_root)
        self.career = Career.objects.create(name='Analista Programador', academic_area=self.academic_area)
        self.student = Student.objects.create(
            full_name='Luisa Soto', rut='19.222.111-0', email='luisa@example.com', phone='555', career=self.career
        )
        self.category_becas = CaseCategory.objects.create(name='Becas y beneficios')
        self.category_practica = CaseCategory.objects.create(name='Práctica')

        self.user = User.objects.create_user('becas_user', password='test123')
        self.user.profile.area = self.area
        self.user.profile.role = UserProfile.Role.SCHOLARSHIP_MANAGER
        self.user.profile.save()

    def test_case_form_limits_categories_by_role(self):
        self.client.login(username='becas_user', password='test123')
        response = self.client.get(reverse('cases:create'))
        self.assertEqual(response.status_code, 200)
        available_ids = list(response.context['form'].fields['category'].queryset.values_list('id', flat=True))
        self.assertIn(self.category_becas.id, available_ids)
        self.assertNotIn(self.category_practica.id, available_ids)

    def test_rejects_manual_post_with_forbidden_category(self):
        self.client.login(username='becas_user', password='test123')
        response = self.client.post(
            reverse('cases:create'),
            data={
                'title': 'Caso inválido',
                'description': 'Intento con categoría no permitida',
                'category': self.category_practica.pk,
                'student': self.student.pk,
                'priority': Case.Priority.MEDIUM,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Escoja una opción válida. Esa opción no está entre las disponibles.')
        self.assertFalse(Case.objects.filter(title='Caso inválido').exists())

    def test_ajax_subcategories_load_for_editing(self):
        subcategory = CaseSubcategory.objects.create(category=self.category_practica, name='Práctica dual')
        self.client.login(username='becas_user', password='test123')

        response = self.client.get(
            reverse('cases:ajax_load_subcategories'),
            data={'category_id': self.category_practica.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            [{'id': subcategory.id, 'name': subcategory.name}],
        )
