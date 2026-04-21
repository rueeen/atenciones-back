from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from organization.models import AcademicArea, Area, Career
from students.forms import StudentForm
from students.models import Student


class StudentFormTest(TestCase):
    def setUp(self):
        self.area = Area.objects.create(name='Dirección Académica')
        self.academic_area_1 = AcademicArea.objects.create(name='Informática', area=self.area)
        self.academic_area_2 = AcademicArea.objects.create(name='Salud', area=self.area)
        self.career_1 = Career.objects.create(name='Ingeniería en Informática', academic_area=self.academic_area_1)
        self.career_2 = Career.objects.create(name='Técnico en Enfermería', academic_area=self.academic_area_2)

    def test_form_loads_career_queryset_from_posted_academic_area(self):
        form = StudentForm(data={'academic_area': self.academic_area_1.id})
        self.assertQuerySetEqual(
            form.fields['career'].queryset,
            Career.objects.filter(academic_area=self.academic_area_1).order_by('name'),
            transform=lambda x: x,
        )

    def test_form_invalid_if_career_does_not_belong_to_academic_area(self):
        form = StudentForm(
            data={
                'full_name': 'Estudiante Demo',
                'rut': '12.345.678-9',
                'email': 'demo@example.com',
                'phone': '+56 912345678',
                'academic_area': self.academic_area_1.id,
                'career': self.career_2.id,
                'schedule': Student.DIURNO,
                'observations': '',
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('career', form.errors)

    def test_form_sets_academic_area_initial_on_update(self):
        student = Student.objects.create(
            full_name='Estudiante Edit',
            rut='11.111.111-1',
            email='edit@example.com',
            phone='123456',
            career=self.career_1,
            schedule=Student.DIURNO,
        )

        form = StudentForm(instance=student)

        self.assertEqual(form.fields['academic_area'].initial, self.academic_area_1)
        self.assertIn(self.career_1, form.fields['career'].queryset)


class StudentAjaxViewsTest(TestCase):
    def setUp(self):
        self.area = Area.objects.create(name='Dirección Académica')
        self.academic_area = AcademicArea.objects.create(name='Informática', area=self.area)
        self.career = Career.objects.create(name='Ingeniería en Informática', academic_area=self.academic_area)

        self.user = get_user_model().objects.create_user(
            username='tester',
            email='tester@example.com',
            password='secret123',
        )
        self.client.login(username='tester', password='secret123')

    def test_careers_by_academic_area_returns_careers(self):
        response = self.client.get(
            reverse('students:careers_by_academic_area'),
            {'academic_area_id': self.academic_area.id},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload['careers']), 1)
        self.assertEqual(payload['careers'][0]['id'], self.career.id)

    def test_careers_by_academic_area_returns_400_for_invalid_id(self):
        response = self.client.get(
            reverse('students:careers_by_academic_area'),
            {'academic_area_id': 'abc'},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['careers'], [])

    def test_modal_create_form_contains_dependency_attributes(self):
        response = self.client.get(reverse('students:modal_create'))

        self.assertEqual(response.status_code, 200)
        html = response.json()['html']
        self.assertIn('data-student-form="true"', html)
        self.assertIn(reverse('students:careers_by_academic_area'), html)


class StudentModelTest(TestCase):
    def test_student_str(self):
        area = Area.objects.create(name='Dirección Académica')
        academic_area = AcademicArea.objects.create(name='Informática', area=area)
        career = Career.objects.create(name='Ingeniería en Informática', academic_area=academic_area)
        student = Student.objects.create(
            full_name='Test',
            rut='22.222.222-2',
            email='t@test.com',
            phone='1',
            career=career,
            schedule=Student.DIURNO,
        )

        self.assertIn('Test', str(student))
