# Generated by Django 4.2 on 2025-03-27 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('augmentations', '0004_versionimageaugmentation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='versionimageaugmentation',
            name='augmentation_name',
            field=models.CharField(max_length=255),
        ),
    ]
