from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cases', '0002_alter_casetransfer_options'),
        ('psychopedagogy', '0002_psychopedagogyrecord_unique_active_psychopedagogy_record_per_student'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=180)),
                ('message', models.TextField()),
                ('notification_type', models.CharField(choices=[('case_created', 'Caso creado'), ('case_assigned', 'Caso asignado'), ('case_transferred', 'Caso transferido'), ('case_closed', 'Caso cerrado'), ('case_comment', 'Comentario en caso'), ('case_attachment', 'Adjunto en caso'), ('psy_record_updated', 'Actualización de ficha psicopedagógica'), ('psy_log_created', 'Bitácora psicopedagógica creada'), ('psy_attachment', 'Adjunto psicopedagógico')], max_length=40)),
                ('action_url', models.CharField(blank=True, max_length=255)),
                ('is_read', models.BooleanField(default=False)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('case', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='cases.case')),
                ('psychopedagogy_log_entry', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='psychopedagogy.psychopedagogylogentry')),
                ('psychopedagogy_record', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='psychopedagogy.psychopedagogyrecord')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['user', 'is_read', '-created_at'], name='notificatio_user_id_2f8f2d_idx'), models.Index(fields=['notification_type', '-created_at'], name='notificatio_notific_a05655_idx')],
            },
        ),
    ]
