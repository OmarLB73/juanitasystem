# Generated by Django 5.0 on 2025-03-22 15:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyect', '0076_remove_item_proyect_item_workorder'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='proyect',
        ),
        migrations.AddField(
            model_name='event',
            name='workorder',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='proyect.workorder'),
        ),
    ]
