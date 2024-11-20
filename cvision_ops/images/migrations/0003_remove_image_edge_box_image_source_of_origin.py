# Generated by Django 4.2 on 2024-11-17 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0002_image_edge_box_alter_image_image_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='edge_box',
        ),
        migrations.AddField(
            model_name='image',
            name='source_of_origin',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]