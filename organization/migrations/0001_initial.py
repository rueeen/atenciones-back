from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('name', models.CharField(max_length=120, unique=True)), ('is_academic_direction', models.BooleanField(default=False))],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='AcademicArea',
            fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('name', models.CharField(max_length=160, unique=True)), ('parent_area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='academic_areas', to='organization.area'))],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Career',
            fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('name', models.CharField(max_length=180, unique=True)), ('academic_area', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='careers', to='organization.academicarea'))],
            options={'ordering': ['name']},
        ),
    ]
