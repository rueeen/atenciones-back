from django.contrib.auth.models import User
from django.test import TestCase

from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from accounts.services import visible_cases_for
from cases.models import Case, CaseCategory
from organization.models import AcademicArea, Area, Career
from students.models import Student


class UserProfileFormValidationTest(TestCase):
    def setUp(self):
        self.daf = Area.objects.create(name='DAF')
        self.dac = Area.objects.create(name='DAC')
        self.academic_area = AcademicArea.objects.create(name='Tecnología', area=self.dac)
        self.career = Career.objects.create(name='Informática', academic_area=self.academic_area)

    def test_non_academic_role_cannot_have_academic_scope(self):
        form = UserProfileForm(data={
            'area': self.daf.id,
            'role': UserProfile.Role.STAFF,
            'academic_area': self.academic_area.id,
            'careers': [self.career.id],
        })
        self.assertFalse(form.is_valid())
        self.assertIn('academic_area', form.errors)
        self.assertIn('careers', form.errors)


class AcademicVisibilityRulesTest(TestCase):
    def setUp(self):
        self.dac = Area.objects.create(name='DAC')
        self.academic_area = AcademicArea.objects.create(name='Tecnología', area=self.dac)
        self.career_1 = Career.objects.create(name='Informática', academic_area=self.academic_area)
        self.career_2 = Career.objects.create(name='Ciberseguridad', academic_area=self.academic_area)
        self.student_1 = Student.objects.create(
            full_name='A', rut='10.000.000-1', email='a@example.com', phone='111', career=self.career_1
        )
        self.student_2 = Student.objects.create(
            full_name='B', rut='10.000.000-2', email='b@example.com', phone='222', career=self.career_2
        )
        self.category = CaseCategory.objects.create(name='Académico')
        self.user = User.objects.create_user('director', password='test123')
        profile = self.user.profile
        profile.role = UserProfile.Role.CAREER_DIRECTOR
        profile.area = self.dac
        profile.academic_area = self.academic_area
        profile.save()
        profile.careers.set([self.career_1, self.career_2])

        self.case_1 = Case.objects.create(
            title='Caso 1',
            description='Detalle',
            category=self.category,
            student=self.student_1,
            created_by=self.user,
            origin_area=self.dac,
            current_area=self.dac,
        )
        self.case_2 = Case.objects.create(
            title='Caso 2',
            description='Detalle',
            category=self.category,
            student=self.student_2,
            created_by=self.user,
            origin_area=self.dac,
            current_area=self.dac,
        )

    def test_career_director_can_see_multiple_careers(self):
        qs = visible_cases_for(self.user)
        self.assertIn(self.case_1, qs)
        self.assertIn(self.case_2, qs)
