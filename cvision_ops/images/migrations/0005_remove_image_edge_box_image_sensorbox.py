# Generated by Django 4.2 on 2024-12-16 16:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0003_sensorbox'),
        ('images', '0004_image_edge_box'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='edge_box',
        ),
        migrations.AddField(
            model_name='image',
            name='sensorbox',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tenants.sensorbox'),
        ),
    ]
