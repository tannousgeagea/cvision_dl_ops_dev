# Generated by Django 4.2 on 2025-04-21 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_job_image_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='status',
            field=models.CharField(choices=[('unassigned', 'Unassigned'), ('assigned', 'Assigned'), ('in_review', 'In Review'), ('completed', 'Completed'), ('sliced', 'Sliced')], default='unassigned', max_length=20),
        ),
    ]
