# Generated by Django 4.2 on 2025-06-12 19:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('projects', '0016_projectimage_job_assignment_status'),
        ('ml_models', '0005_modeltag_model_tags'),
        ('images', '0006_tag_imagetag_image_tags'),
    ]

    operations = [
        migrations.CreateModel(
            name='PredictionImageResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inference_time', models.FloatField(blank=True, help_text='Time taken to run inference (in seconds)', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('dataset_version', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prediction_results', to='projects.version')),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prediction_results', to='images.image')),
                ('model_version', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prediction_results', to='ml_models.modelversion')),
            ],
            options={
                'verbose_name_plural': 'Prediction Image Results',
                'db_table': 'prediction_image_result',
                'unique_together': {('model_version', 'dataset_version', 'image')},
            },
        ),
        migrations.CreateModel(
            name='PredictionOverlay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_label', models.CharField(max_length=255)),
                ('confidence', models.FloatField(default=0.0)),
                ('bbox', models.JSONField(blank=True, help_text='Bounding box format: [x_min, y_min, x_max, y_max] (normalized)', null=True)),
                ('mask', models.JSONField(blank=True, help_text='Optional segmentation mask (e.g., polygon or RLE)', null=True)),
                ('overlay_type', models.CharField(choices=[('bbox', 'Bounding Box'), ('mask', 'Segmentation Mask')], default='bbox', max_length=50)),
                ('matched_gt', models.BooleanField(default=False, help_text='Whether this prediction matched a ground-truth annotation (for metric eval)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('prediction_result', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='overlays', to='inferences.predictionimageresult')),
            ],
            options={
                'verbose_name_plural': 'Prediction Overlays',
                'db_table': 'prediction_overlay',
            },
        ),
    ]
