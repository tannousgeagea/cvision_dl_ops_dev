# Generated by Django 4.2 on 2024-11-22 14:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('images', '0004_image_edge_box'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('meta_info', models.JSONField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Project Type',
                'db_table': 'project_type',
            },
        ),
        migrations.CreateModel(
            name='Visibility',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Visibility',
                'db_table': 'visibility',
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('thumbnail_url', models.URLField(blank=True, null=True)),
                ('last_edited', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('project_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='projects.projecttype')),
                ('visibility', models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to='projects.visibility')),
            ],
            options={
                'verbose_name_plural': 'Projects',
                'db_table': 'project',
            },
        ),
        migrations.CreateModel(
            name='ProjectMetadata',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=100)),
                ('value', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='projects.project')),
            ],
            options={
                'verbose_name_plural': 'Project Metadata',
                'db_table': 'project_metadata',
                'unique_together': {('project', 'key')},
            },
        ),
        migrations.CreateModel(
            name='ProjectImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('annotated', models.BooleanField(default=False)),
                ('annotations', models.JSONField(blank=True, null=True)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='images.image')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_images', to='projects.project')),
            ],
            options={
                'verbose_name_plural': 'Project Images',
                'db_table': 'project_image',
                'unique_together': {('project', 'image')},
            },
        ),
    ]