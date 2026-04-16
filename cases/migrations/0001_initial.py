from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import cases.models


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL), ('organization', '0001_initial'), ('students', '0001_initial')]

    operations = [
        migrations.CreateModel(
            name='CaseCategory',
            fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('name', models.CharField(max_length=120, unique=True))],
        ),
        migrations.CreateModel(
            name='CaseSubcategory',
            fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('name', models.CharField(max_length=120)), ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='cases.casecategory'))],
            options={'unique_together': {('category', 'name')}},
        ),
        migrations.CreateModel(
            name='Case',
            fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('folio', models.CharField(editable=False, max_length=20, unique=True)), ('title', models.CharField(max_length=200)), ('description', models.TextField()), ('priority', models.CharField(choices=[('low', 'Baja'), ('medium', 'Media'), ('high', 'Alta'), ('urgent', 'Urgente')], default='medium', max_length=10)), ('status', models.CharField(choices=[('open', 'Abierto'), ('in_review', 'En revisión'), ('transferred', 'Derivado'), ('pending_info', 'Pendiente de información'), ('pending_area', 'Pendiente de otra área'), ('resolved', 'Resuelto'), ('closed', 'Cerrado'), ('rejected', 'Rechazado')], default='open', max_length=20)), ('due_date', models.DateField(blank=True, null=True)), ('final_resolution', models.TextField(blank=True)), ('closed_at', models.DateTimeField(blank=True, null=True)), ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)), ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cases', to='cases.casecategory')), ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cases_created', to=settings.AUTH_USER_MODEL)), ('current_area', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='assigned_cases', to='organization.area')), ('current_assignee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cases_assigned', to=settings.AUTH_USER_MODEL)), ('origin_area', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='origin_cases', to='organization.area')), ('student', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cases', to='students.student')), ('subcategory', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cases', to='cases.casesubcategory'))],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='CaseTransfer',
            fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('note', models.TextField()), ('created_at', models.DateTimeField(auto_now_add=True)), ('case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfers', to='cases.case')), ('from_area', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='transfers_out', to='organization.area')), ('to_area', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='transfers_in', to='organization.area')), ('transferred_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='case_transfers', to=settings.AUTH_USER_MODEL))],
        ),
        migrations.CreateModel(
            name='CaseHistory',
            fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('event_type', models.CharField(choices=[('created', 'Creación'), ('status_changed', 'Cambio de estado'), ('assignee_changed', 'Cambio de responsable'), ('transferred', 'Derivación'), ('comment', 'Comentario'), ('attachment', 'Adjunto'), ('closed', 'Cierre')], max_length=30)), ('description', models.TextField()), ('created_at', models.DateTimeField(auto_now_add=True)), ('actor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='case_history_events', to=settings.AUTH_USER_MODEL)), ('case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='cases.case'))],
            options={'ordering': ['created_at']},
        ),
        migrations.CreateModel(
            name='CaseComment',
            fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('comment', models.TextField()), ('is_internal', models.BooleanField(default=True)), ('created_at', models.DateTimeField(auto_now_add=True)), ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='case_comments', to=settings.AUTH_USER_MODEL)), ('case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='cases.case'))],
            options={'ordering': ['created_at']},
        ),
        migrations.CreateModel(
            name='CaseAttachment',
            fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('file', models.FileField(upload_to=cases.models.case_attachment_path, validators=[cases.models.validate_file_extension])), ('uploaded_at', models.DateTimeField(auto_now_add=True)), ('case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='cases.case')), ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='case_attachments', to=settings.AUTH_USER_MODEL))],
        ),
    ]
