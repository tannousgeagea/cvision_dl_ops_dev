# Generated by Django 4.2 on 2025-03-11 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0011_version_version_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectimage',
            name='feedback_provided',
            field=models.BooleanField(default=False),
        ),
    ]
