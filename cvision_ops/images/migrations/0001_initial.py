# Generated by Django 4.2 on 2024-11-17 10:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ImageMode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mode', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('meta_info', models.JSONField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Image Mode',
                'db_table': 'image_mode',
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_id', models.CharField(max_length=255)),
                ('image_name', models.CharField(max_length=255)),
                ('image_file', models.ImageField(upload_to='images/')),
                ('annotated', models.BooleanField(default=False)),
                ('processed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('meta_info', models.JSONField(blank=True, null=True)),
                ('mode', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='images.imagemode')),
            ],
            options={
                'verbose_name_plural': 'Images',
                'db_table': 'image',
            },
        ),
    ]