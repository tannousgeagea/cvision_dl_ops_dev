# Generated by Django 4.2 on 2025-03-25 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotations', '0006_annotation_feedback_provided'),
    ]

    operations = [
        migrations.AddField(
            model_name='annotation',
            name='annotation_source',
            field=models.CharField(choices=[('manual', 'Manual Annotation'), ('prediction', 'Model Prediction')], default='manual', help_text='Indicates whether the annotation was created manually or generated by a model.', max_length=20),
        ),
    ]
