from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL), ('organization', '0001_initial')]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('role', models.CharField(choices=[('admin', 'Administrador general'), ('supervisor', 'Supervisor de área'), ('staff', 'Funcionario'), ('career_director', 'Director de carrera'), ('career_coordinator', 'Coordinador de carrera'), ('read_only', 'Solo lectura')], default='staff', max_length=30)), ('area', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='profiles', to='organization.area')), ('career', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='profiles', to='organization.career')), ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL))],
        ),
    ]
