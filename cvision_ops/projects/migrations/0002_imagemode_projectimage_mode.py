# Generated by Django 4.2 on 2024-12-18 08:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
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
        migrations.AddField(
            model_name='projectimage',
            name='mode',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='projects.imagemode'),
        ),
    ]
