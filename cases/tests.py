from django.contrib.auth.models import User
from django.test import TestCase

from accounts.models import UserProfile
from accounts.services import visible_cases_for
from cases.models import Case, CaseCategory
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
