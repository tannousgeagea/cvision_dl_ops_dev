# Generated by Django 4.2 on 2025-01-30 11:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0009_projectimage_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='versionimage',
            name='version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='version_images', to='projects.version'),
        ),
    ]
