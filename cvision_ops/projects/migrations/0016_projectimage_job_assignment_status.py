# Generated by Django 4.2 on 2025-04-22 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0015_project_organization'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectimage',
            name='job_assignment_status',
            field=models.CharField(choices=[('assigned', 'Assigned to job'), ('waiting', 'Waiting for job'), ('excluded', 'Excluded from job assignment')], default='waiting', help_text='Tracks whether this image is already in a job or still pending assignment.', max_length=20),
        ),
    ]
