# Generated by Django 4.2 on 2025-05-11 13:41

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import ml_models.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('projects', '0016_projectimage_job_assignment_status'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ModelFramework',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Model Frameworks',
                'db_table': 'model_framework',
            },
        ),
        migrations.CreateModel(
            name='ModelTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Model Tasks',
                'db_table': 'model_task',
            },
        ),
        migrations.CreateModel(
            name='Model',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('framework', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='ml_models.modelframework')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='models', to='projects.project')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='ml_models.modeltask')),
            ],
            options={
                'verbose_name_plural': 'ML Models',
                'db_table': 'ml_model',
            },
        ),
        migrations.CreateModel(
            name='ModelVersion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.CharField(max_length=50)),
                ('checkpoint', models.FileField(blank=True, max_length=1024, null=True, upload_to=ml_models.models.get_model_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pt', 'pth', 'h5', 'onnx'])])),
                ('config', models.JSONField(blank=True, null=True)),
                ('metrics', models.JSONField(blank=True, null=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('training', 'Training'), ('trained', 'Trained'), ('failed', 'Failed'), ('deployed', 'Deployed')], default='draft', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('dataset_version', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='trained_models', to='projects.version')),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='versions', to='ml_models.model')),
            ],
            options={
                'verbose_name_plural': 'Model Versions',
                'db_table': 'model_verison',
                'unique_together': {('model', 'version')},
            },
        ),
    ]
