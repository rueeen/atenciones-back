from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [('organization', '0001_initial')]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('full_name', models.CharField(max_length=200)), ('rut', models.CharField(max_length=12, unique=True)), ('email', models.EmailField(max_length=254)), ('phone', models.CharField(max_length=30)), ('schedule', models.CharField(blank=True, max_length=60)), ('observations', models.TextField(blank=True)), ('created_at', models.DateTimeField(auto_now_add=True)), ('career', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='students', to='organization.career'))],
            options={'ordering': ['full_name']},
        ),
    ]
