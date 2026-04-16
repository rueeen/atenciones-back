from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from accounts.models import UserProfile
from cases.models import CaseCategory
from organization.models import AcademicArea, Area, Career


class Command(BaseCommand):
    help = 'Carga datos base institucionales, categorías y usuarios de ejemplo.'

    def handle(self, *args, **options):
        dae, _ = Area.objects.get_or_create(name='DAE', defaults={'is_academic_direction': False})
        dir_acad, _ = Area.objects.get_or_create(name='Dirección Académica', defaults={'is_academic_direction': True})

        areas = [
            'Administración', 'Gastronomía', 'Turismo y Hospitalidad', 'Construcción', 'Energía', 'Logística',
            'Mecánica', 'Automatización, Electrónica y Robótica', 'Diseño e Industria Digital',
            'Informática, Ciberseguridad y Telecomunicaciones',
        ]
        aa_map = {}
        for name in areas:
            aa_map[name], _ = AcademicArea.objects.get_or_create(name=name, parent_area=dir_acad)

        careers = {
            'Administración': ['Administración de Empresas', 'Comercio Exterior', 'Ingeniería en Administración de Empresas'],
            'Gastronomía': ['Gastronomía'],
            'Turismo y Hospitalidad': ['Gestión Turística'],
            'Construcción': ['Construcción Civil', 'Técnico en Construcción', 'Técnico en Topografía y Geomática'],
            'Energía': ['Técnico en Electricidad Industrial'],
            'Logística': ['Técnico en Logística'],
            'Mecánica': ['Ingeniería en Mecánica y Electromovilidad Automotriz', 'Técnico en Mecánica y Electromovilidad Automotriz'],
            'Automatización, Electrónica y Robótica': ['Ingeniería en Automatización y Robótica', 'Técnico en Automatización y Robótica'],
            'Diseño e Industria Digital': ['Diseño Digital Profesional', 'Diseño Digital y Web'],
            'Informática, Ciberseguridad y Telecomunicaciones': ['Analista Programador', 'Ingeniería en Informática'],
        }
        for area_name, names in careers.items():
            for name in names:
                Career.objects.get_or_create(name=name, academic_area=aa_map[area_name])

        for category in [
            'Becas y beneficios', 'Vida estudiantil', 'Inscripción o matrícula', 'Solicitudes académicas',
            'Certificados', 'Convalidaciones', 'Horarios', 'Titulación', 'Práctica', 'Documentación', 'Otros',
        ]:
            CaseCategory.objects.get_or_create(name=category)

        admin, created = User.objects.get_or_create(username='admin')
        if created:
            admin.set_password('admin1234')
            admin.is_superuser = True
            admin.is_staff = True
            admin.save()
        admin.profile.area = dir_acad
        admin.profile.role = UserProfile.Role.ADMIN
        admin.profile.save()

        sup, created = User.objects.get_or_create(username='supervisor_dae', defaults={'first_name': 'Supervisor', 'last_name': 'DAE'})
        if created:
            sup.set_password('supervisor1234')
            sup.save()
        sup.profile.area = dae
        sup.profile.role = UserProfile.Role.SUPERVISOR
        sup.profile.save()

        self.stdout.write(self.style.SUCCESS('Datos iniciales cargados correctamente.'))
