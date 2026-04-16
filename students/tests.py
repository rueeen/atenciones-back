from django.test import TestCase
from organization.models import Area, AcademicArea, Career
from students.models import Student


class StudentModelTest(TestCase):
    def test_student_str(self):
        root = Area.objects.create(name='Dirección Académica', is_academic_direction=True)
        aa = AcademicArea.objects.create(name='Informática', parent_area=root)
        career = Career.objects.create(name='Ingeniería en Informática', academic_area=aa)
        student = Student.objects.create(full_name='Test', rut='22.222.222-2', email='t@test.com', phone='1', career=career)
        self.assertIn('Test', str(student))
