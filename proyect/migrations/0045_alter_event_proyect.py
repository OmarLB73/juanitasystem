# Generated by Django 5.0 on 2025-01-12 21:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyect', '0044_remove_event_proyect_id_event_proyect_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='proyect',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='proyect.proyect'),
        ),
    ]
